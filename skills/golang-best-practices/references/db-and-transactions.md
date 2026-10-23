# Database, Transactions, Migrations, Pool

Check `go.mod` first: if the project uses sqlc, sqlx, ent, bun, or pgx directly, extend that instead of introducing GORM. Choose per project: `database/sql` (or pgx) for explicit SQL and full control; GORM for rapid CRUD with migrations handled separately.

## 1. database/sql Essentials

```go
db, err := sql.Open("pgx", dsn)          // does not connect yet
if err != nil { return err }
if err := db.PingContext(ctx); err != nil { return err }   // verify at startup
defer db.Close()
```

Rules:
- Always use the `...Context` methods (`QueryContext`, `QueryRowContext`, `ExecContext`, `BeginTx`).
- **Parameterized queries only.** Never build SQL with `fmt.Sprintf` from user input.
- Close what you open: `defer rows.Close()` right after a successful `QueryContext`, and check `rows.Err()` after the loop.
- Handle `sql.ErrNoRows` explicitly with `errors.Is`; translate to a domain error.
- Scan nullable columns into `sql.Null*` types or pointers.
- Do not hold a `Rows` open while doing other queries on the same transaction.

```go
func (s *Store) ListByOwner(ctx context.Context, owner string) ([]Item, error) {
	rows, err := s.db.QueryContext(ctx, `SELECT id, name FROM items WHERE owner = $1`, owner)
	if err != nil {
		return nil, fmt.Errorf("list items: %w", err)
	}
	defer rows.Close()

	items := make([]Item, 0, 16)
	for rows.Next() {
		var it Item
		if err := rows.Scan(&it.ID, &it.Name); err != nil {
			return nil, fmt.Errorf("scan item: %w", err)
		}
		items = append(items, it)
	}
	return items, rows.Err()
}
```

## 2. Transactions

Principles: one transaction per use case; keep it short; no network calls or user waiting inside; always roll back on error or panic; pass the transaction to every statement that belongs to it.

### Plain database/sql helper
```go
func WithTx(ctx context.Context, db *sql.DB, fn func(tx *sql.Tx) error) (err error) {
	tx, err := db.BeginTx(ctx, nil)
	if err != nil {
		return fmt.Errorf("begin tx: %w", err)
	}
	defer func() {
		if p := recover(); p != nil {
			_ = tx.Rollback()
			panic(p)
		}
		if err != nil {
			if rbErr := tx.Rollback(); rbErr != nil && !errors.Is(rbErr, sql.ErrTxDone) {
				err = errors.Join(err, fmt.Errorf("rollback: %w", rbErr))
			}
		}
	}()
	if err = fn(tx); err != nil {
		return err
	}
	if err = tx.Commit(); err != nil {
		return fmt.Errorf("commit: %w", err)
	}
	return nil
}
```

### GORM closure (automatic commit/rollback)
```go
func Transfer(ctx context.Context, db *gorm.DB, fromID, toID uint, amount int) error {
	return db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
		res := tx.Model(&Account{}).
			Where("id = ? AND balance >= ?", fromID, amount).
			Update("balance", gorm.Expr("balance - ?", amount))
		if res.Error != nil {
			return res.Error                  // returning an error rolls back
		}
		if res.RowsAffected == 0 {
			return ErrInsufficientFunds
		}
		res = tx.Model(&Account{}).
			Where("id = ?", toID).
			Update("balance", gorm.Expr("balance + ?", amount))
		if res.Error != nil {
			return res.Error
		}
		if res.RowsAffected == 0 {
			return ErrAccountNotFound
		}
		return nil                            // nil commits
	})
}
```
- Use the `tx` handle inside the closure, never the outer `db`.
- Nested `tx.Transaction` creates a savepoint (rolling back only the inner part when it returns an error and the outer returns nil).
- Avoid manual `Begin/Commit/Rollback` unless you need control the closure cannot give.
- Make balance-style updates atomic in SQL (`balance = balance - ?` with a guard) rather than read-modify-write; for read-modify-write use `SELECT ... FOR UPDATE` (`clause.Locking{Strength: "UPDATE"}`) or optimistic version columns.

### Keeping the application layer free of DB types
```go
type TxRunner interface {
	InTx(ctx context.Context, fn func(ctx context.Context) error) error
}
```
The implementation stores the active transaction in the derived context (unexported key) and repositories read it from there. Use only when layering requires it; otherwise pass `*sql.Tx` explicitly in the store layer.

## 3. GORM Setup and Pitfalls

```go
db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{
	Logger:      logger.Default.LogMode(logger.Warn),
	PrepareStmt: true,
})
```
- Always `db.WithContext(ctx)`.
- Check `.Error` on every call; `First` returns `gorm.ErrRecordNotFound` (map to a domain error), `Find` does not.
- `Update` with a struct skips zero values; use `Select(...)` or a map when zeroing fields is intended.
- `Delete` without a condition is blocked by GORM; never bypass with `AllowGlobalUpdate` casually.
- Prevent N+1 with `Preload` or explicit joins; select only needed columns for large rows.
- Hooks (`BeforeCreate`, etc.) are hidden behavior; keep them trivial or avoid them. Business rules belong in services/domain.
- Keep GORM models in the persistence package and map to domain types if you use layered architecture.
- Do not use `AutoMigrate` as the production migration strategy.

## 4. Migrations with Goose

```bash
goose -dir migrations create add_users_table sql
goose -dir migrations postgres "$DATABASE_URL" up
goose -dir migrations postgres "$DATABASE_URL" status
```
```sql
-- migrations/20250115120000_add_users_table.sql
-- +goose Up
CREATE TABLE users (
    id         BIGSERIAL PRIMARY KEY,
    email      TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- +goose Down
DROP TABLE users;
```
Rules:
- One logical change per migration; never edit a migration that has shipped; add a new one.
- Backward-compatible steps for zero-downtime deploys: add nullable column -> deploy code -> backfill -> add constraint; drop columns only after code stops using them.
- Always write and test `Down`, or document why it is irreversible.
- Run migrations as a separate deploy step or at startup behind a lock, not from many replicas at once without coordination.
- Pin the tool version (install a specific `goose` release instead of `@latest`), and keep it in tooling docs or a `tools.go` / `go tool` directive.

## 5. Connection Pool

```go
sqlDB, _ := db.DB()                          // for GORM; with database/sql use db directly
sqlDB.SetMaxOpenConns(50)
sqlDB.SetMaxIdleConns(10)
sqlDB.SetConnMaxIdleTime(5 * time.Minute)
sqlDB.SetConnMaxLifetime(30 * time.Minute)   // below DB / proxy timeouts
```
| Setting | Guidance |
|---|---|
| MaxOpenConns | (DB max connections - admin headroom) / app instances. Default is unlimited, which can exhaust the database |
| MaxIdleConns | About 10-25% of MaxOpenConns; too low causes reconnect churn |
| ConnMaxIdleTime | 5-10 min |
| ConnMaxLifetime | Shorter than server `wait_timeout` or proxy/load balancer idle limits |

Export pool stats (`db.Stats()`) to metrics; watch `WaitCount` and `WaitDuration` for saturation.

## 6. Review Checklist

- [ ] All queries parameterized and context-aware
- [ ] `rows.Close()` deferred, `rows.Err()` checked
- [ ] Multi-statement writes inside one transaction using the tx handle
- [ ] No external calls inside a transaction
- [ ] `ErrNoRows`/`ErrRecordNotFound` mapped to domain errors
- [ ] Pool limits set; migrations versioned with `Down`
