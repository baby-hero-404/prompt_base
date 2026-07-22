# Nest.js Architecture & Design Patterns

## 1. Domain Coverage & Core Components

### Module Architecture & Dependency Injection
- **Execution Order**: Middleware → Guards → Interceptors (before) → Pipes → Route handler → Interceptors (after).
- **Circular Dependencies**: Use `forwardRef()` or refactor shared logic to a common module.
- **Provider Scope**: Default (Singleton), Request (Per-request), Transient (Per-injection).

### Controllers & Request Handling
- **DTOs**: Mandatory for request validation using `class-validator`.
- **Serialization**: Use `@Exclude()` and `@Expose()` via `ClassSerializerInterceptor`.

### Database Integration
- **TypeORM**: Repository pattern, Entity decorators, Query builder.
- **Mongoose**: Schema decorators, Model injection.
- **Prisma**: Database client as a provider.

---

## 2. Advanced Patterns

### Dynamic Module Pattern
```typescript
@Module({})
export class ConfigModule {
  static forRoot(options: ConfigOptions): DynamicModule {
    return {
      module: ConfigModule,
      providers: [{ provide: 'CONFIG', useValue: options }],
      exports: ['CONFIG'],
    };
  }
}
```

### Global Module Pattern
```typescript
@Global()
@Module({
  providers: [GlobalService],
  exports: [GlobalService],
})
export class GlobalModule {}
```

### Custom Decorator Pattern
```typescript
export const Auth = (...roles: Role[]) => 
  applyDecorators(
    UseGuards(JwtAuthGuard, RolesGuard),
    Roles(...roles),
  );
```

---

## 3. Performance & Optimization

- **Caching**: Use `CacheManager` + `CacheInterceptor`.
- **N+1 Problems**: Use **DataLoader** pattern for GraphQL or efficient `.find({ relations: [...] })` for TypeORM.
- **Compression**: `compression` middleware for production.
- **Clustering**: Utilize Node.js Cluster module for multi-core scaling.
