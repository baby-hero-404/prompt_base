# Nest.js Quality Gate & Decision Support

## 1. Code Review Checklist

### Architecture & DI
- [ ] All services have `@Injectable()`.
- [ ] Module boundaries follow domain/feature separation.
- [ ] Circular dependencies avoided (no excessive `forwardRef`).

### Database (TypeORM)
- [ ] Entities registered in `TypeOrmModule.forFeature()`.
- [ ] Named connections used for multiple databases.
- [ ] Migrations handled properly, not just relying on `synchronize: true`.

### Security (JWT)
- [ ] Strategy uses `passport-jwt`.
- [ ] Secret matches exactly between `JwtModule` and Strategy.
- [ ] Proper error handling for expired/invalid tokens.

---

## 2. Decision Trees

### Choosing ORM
- **Migrations/Safety**: Prisma.
- **Complex Relations/Legacy**: TypeORM.
- **NoSQL**: Mongoose.

### Authentication Strategy
- **Stateless/Standard**: JWT with Passport.
- **Stateful/Sessions**: Redis + Express Sessions.
- **OAuth**: Passport Social Strategies.

### Caching Strategy
- **Global Data**: In-memory (internal).
- **User-Specific**: Redis (external).
- **DB Queries**: Result caching via ORM.

---

## 3. Success Metrics

- ✅ All tests pass (Unit, E2E).
- ✅ `npm run build` succeeds (Typecheck).
- ✅ No circular dependencies introduced.
- ✅ API Documentation (Swagger) updated.
