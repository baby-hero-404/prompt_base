# Nest.js Troubleshooting & Common Issues

## 1. High-Frequency Issues

### "Nest can't resolve dependencies" (Constructor injection errors)
- **Identify**: The `?` in the error message indicates the position of the missing dependency.
- **Fix**: Check `providers` array in the current module or `imports` if from another module. Verify `@Injectable()` decorator.

### "Circular dependency detected"
- **Quick Fix**: `forwardRef()` on BOTH sides.
- **Long-term Fix**: Extract shared logic to a separate module.

### "Unable to connect to database" (TypeORM)
- **Misleading Cause**: Entity syntax errors (e.g., `@Column` without `@Entity`) often throw connection errors.
- **Action**: Check entity decorators and ensure `synchronize: true` is safe for the environment.

### "Unauthorized 401 (Missing credentials)" (JWT)
- **Fix**: Verify "Bearer [token]" format in header. Check if Strategy is imported from `passport-jwt`.

---

## 2. Testing Case Studies

### E2E dependency resolution
- **Solution**: Use `Test.createTestingModule().compile()` and ensure all external services (Jwt, DB) are mocked specifically for the test context.
- **Mocks**: Use `@golevelup/ts-jest` for automated interface mocking.

### Repository Testing
- **Token**: Use `getRepositoryToken(Entity)` to provide mocked repositories in test modules.

---

## 3. Configuration Regressions

### "secretOrPrivateKey must have a value"
- Ensure `ConfigModule` is loaded *before* `JwtModule` if using `ConfigService` in `useFactory`.

---

## 4. Production Performance

### Memory Leaks
- **Clean up**: Remove event listeners in `onModuleDestroy()`.
- **Diagnostics**: Profile with `node --inspect`.
