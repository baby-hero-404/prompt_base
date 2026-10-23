# Modern Dart (3.x) for Flutter Code

Check the SDK constraint in `pubspec.yaml` (`environment: sdk:`) before using a feature. Records, patterns and sealed classes need Dart 3.0+. Primary constructors need a very recent SDK (see section 5).

## 1. Records

Return several values without a throwaway class.
```dart
(int, int) minMax(List<int> xs) => (xs.reduce(min), xs.reduce(max));
final (lo, hi) = minMax(values);

({String name, int age}) user = (name: 'Ada', age: 36);
print(user.name);
```
Use a real class once the shape has behaviour, is public API, or is reused widely.

## 2. Patterns: When to Use Which

| Situation | Pattern |
|---|---|
| Validate and destructure decoded JSON | Map/List/Object pattern in `switch` or `if-case` |
| URL or path segments | List pattern with rest: `['api', 'users', final id]`, `['assets', ...final rest]` |
| Multiple return values | Record pattern: `final (a, b) = f();` |
| Unpack 3+ fields of an object | Object pattern: `final Point(:x, :y) = p;` |
| Type-specific behaviour over a closed set | Object patterns + `sealed` class (compiler checks exhaustiveness) |
| Range checks | Relational: `case >= 0 && < 10:` |
| Shared case body | Logical-or: `case A() || B():` (same variables in both) |
| Ignore a value | Wildcard `_` |

```dart
// destructure + validate in one step
if (json case {'id': int id, 'name': String name}) {
  return User(id: id, name: name);
}

// switch expression: produces a value, must be exhaustive, no fallthrough
String label(int status) => switch (status) {
      200 || 201 => 'ok',
      >= 400 && < 500 => 'client error',
      >= 500 => 'server error',
      _ => 'unknown',
    };
```

Switch **statement** is for side effects (empty cases fall through, non-empty cases do not need `break`); switch **expression** is for values.

### Keep It Pragmatic
- For one promotable variable, plain `is` promotion is clearer than an `if-case` alias:
```dart
if (key is String && value != null) process(key, value);   // good
// avoid: if (key case String k when value != null) process(k, value);
```
- Do not use patterns for a single call passthrough; use object patterns when you unpack 3+ fields or need nullable promotion across several statements.
- Do not replace simple `.length` checks with list patterns when it makes the code longer.

## 3. Sealed Classes for State and Results

Model UI/result states as a closed hierarchy instead of nullable fields plus booleans.

```dart
sealed class Result<T> {
  const Result();
}
final class Ok<T> extends Result<T> {
  const Ok(this.value);
  final T value;
}
final class Err<T> extends Result<T> {
  const Err(this.error);
  final Object error;
}

Widget view(Result<User> r) => switch (r) {
      Ok(:final value) => ProfileCard(user: value),
      Err(:final error) => ErrorView(error: error),
    };   // adding a new subtype breaks compilation here: that is the point
```
Use for repository return values (`Result<T>` rather than throwing across layers where you want explicit handling), Bloc states, and routes of an on-screen state machine.

## 4. Other Dart 3 Features Worth Using

- **Class modifiers:** `final class` (no subclassing outside library), `interface class`, `base class`, `mixin class`. Mark domain models `final class` to prevent accidental inheritance.
- **Enhanced enums:** fields, methods, `const` constructors on enums for fixed sets with data.
- **Extension types:** zero-cost wrappers for type safety (`extension type const UserId(String value)`).
- **Null safety idioms:** prefer `?.`, `??`, `??=`, and `!` only when a prior check proves non-null. Never sprinkle `!` to silence the analyzer.
- **Cascades and collection `if`/`for`:** `[...a, if (cond) b, for (final x in xs) f(x)]` in widget child lists.
- **Immutability:** `final` fields, `const` constructors, new collections instead of mutation, `copyWith`.
- **Naming and lints:** follow Effective Dart; enable `flutter_lints` (or `very_good_analysis`) in `analysis_options.yaml` and keep `flutter analyze` at zero issues.

## 5. Primary Constructors (new; verify SDK first)

Declares fields and the constructor in the class header. Availability: enabled by default from Dart 3.13; experimental on 3.12 (needs `analyzer: enable-experiment: [primary-constructors]` in `analysis_options.yaml` and `--enable-experiment=primary-constructors`); unsupported before. If the SDK constraint is lower, use the classic form.

```dart
class const Point(final int x, final int y);               // const, final fields

class User(final String id, final String name) {
  // in-body members and initializers go here
}
```
Parameter kinds: `final`/`var` declares a field; `this.x`/`super.x` initializes an existing field/super parameter; a plain parameter is only visible to initializers. Extension types must use primary constructors. Do not migrate a whole codebase unprompted; use it for new code when the project's SDK allows.

## 6. Anti-Patterns

- `dynamic` where a record, sealed class, or typed map would do.
- Catch-all `catch (e)` that swallows errors; catch specific types and rethrow or map to a `Result`.
- `late` fields used to avoid designing initialization (leads to `LateInitializationError`).
- Using `!` after `jsonDecode` instead of validating the shape with a pattern.
- Extending a state/event hierarchy that is not `sealed`, losing exhaustiveness checks.
