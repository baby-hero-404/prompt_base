# Testing

## Pyramid

```
        Integration   few: critical end-to-end flows, real device/emulator
      Widget          many: one screen or component, fast, no device
    Unit              most: models, repositories, view models, pure Dart
```

Write the unit tests for the ViewModel/Repository first (R11: success and failure paths), then a widget test per screen, then integration tests only for flows that must never break (login, checkout).

## Layout

```text
test/
├── data/            # repository, service, model tests
├── ui/              # widget tests mirroring lib/ui
├── helpers/         # pumpApp(), fakes, test data builders
└── goldens/         # golden images (committed)
integration_test/    # flows run on device
```

File names end in `_test.dart`. Add `flutter_test` (and `integration_test`) under `dev_dependencies` with `sdk: flutter`.

## Unit Tests

Prefer **fakes** (small hand-written implementations) for repositories you own; use mocks (`mockito` + `build_runner`, or `mocktail` with no codegen) when interaction verification matters or the dependency is large.

```dart
void main() {
  group('UserRepository', () {
    late FakeApiClient api;
    late UserRepository repo;

    setUp(() {
      api = FakeApiClient();
      repo = UserRepository(apiClient: api);
    });

    test('maps API model to domain model', () async {
      api.nextUser = const UserApiModel(id: '1', fullName: 'Ada');
      expect(await repo.getUser('1'), const User(id: '1', name: 'Ada'));
    });

    test('propagates failure instead of returning null', () {
      api.nextError = Exception('500');
      expect(repo.getUser('1'), throwsException);
    });
  });
}
```

Model serialization pair (both directions plus a bad input):

```dart
test('fromJson/toJson round trip', () {
  final json = {'id': '1', 'name': 'Ada'};
  expect(User.fromJson(json).toJson(), json);
});
test('fromJson rejects wrong type', () {
  expect(() => User.fromJson({'id': 1}), throwsA(isA<TypeError>()));
});
```

ViewModel / Notifier: assert state transitions (`loading` -> `data`, `loading` -> `error`), not implementation details. Use `fakeAsync` (`package:fake_async`) or `tester` for timers.

## Widget Tests

Task Progress:
- [ ] `testWidgets('what the user sees/does', (tester) async { ... })`
- [ ] `await tester.pumpWidget(...)` wrapped in `MaterialApp` (or a shared `pumpApp` helper adding theme, l10n, providers)
- [ ] Locate with `find.text`, `find.byType`, `find.byKey(const ValueKey('submit'))`, `find.bySemanticsLabel`
- [ ] Assert initial state with `expect(finder, findsOneWidget)`
- [ ] Interact: `tap`, `enterText`, `drag`, `scrollUntilVisible`
- [ ] Rebuild: `await tester.pump()` (one frame) or `await tester.pumpAndSettle()` (until animations end)
- [ ] Assert new state
- [ ] **Validator loop:** `flutter test test/ui/login_test.dart` -> read failure -> fix widget or assertion -> re-run

```dart
testWidgets('submit disabled until email valid', (tester) async {
  await tester.pumpWidget(const MaterialApp(home: LoginForm()));

  final button = find.widgetWithText(ElevatedButton, 'Sign in');
  expect(tester.widget<ElevatedButton>(button).onPressed, isNull);

  await tester.enterText(find.byKey(const ValueKey('email')), 'a@b.co');
  await tester.pump();

  expect(tester.widget<ElevatedButton>(button).onPressed, isNotNull);
});
```

Pump rules:
| Situation | Call |
|---|---|
| Static render | `pumpWidget`, then `expect` |
| `setState` after tap | `tap` + `pump()` |
| Animation or transition that ends | `pumpAndSettle()` |
| Infinite animation (spinner, shimmer) | `pump(const Duration(milliseconds: 100))`, never `pumpAndSettle` (it times out) |
| Long or lazy list | `scrollUntilVisible(item, 500, scrollable: listFinder)` before interacting |

Other rules:
- Do not test private widgets or `build` internals; test visible behaviour.
- Give interactive widgets `ValueKey`s used by both app code and tests.
- Override providers/dependencies instead of using real network or storage.
- Set a surface size for responsive tests: `tester.view.physicalSize = const Size(1200, 800); addTearDown(tester.view.reset);`.
- Silence HTTP: widget tests block real `HttpClient`; inject fakes.

## Golden Tests

Catch unintended visual change on stable, important components.

```dart
testWidgets('PriceTag golden', (tester) async {
  await tester.pumpWidget(const MaterialApp(home: Scaffold(body: PriceTag(cents: 1999))));
  await expectLater(find.byType(PriceTag), matchesGoldenFile('goldens/price_tag.png'));
});
```
Generate/update: `flutter test --update-goldens`. Fonts and platform rendering differ across OSes; generate and compare on the **same OS in CI**, or use a golden toolkit and load fonts. Review golden diffs as code. Do not golden-test whole screens with network images or animations.

## Integration Tests

Setup:
```bash
flutter pub add 'dev:integration_test:{"sdk":"flutter"}'
```
```dart
// integration_test/app_test.dart
void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('login then see home', (tester) async {
    app.main();
    await tester.pumpAndSettle();
    await tester.enterText(find.byKey(const ValueKey('email')), 'a@b.co');
    await tester.tap(find.byKey(const ValueKey('login_button')));
    await tester.pumpAndSettle();
    expect(find.text('Welcome'), findsOneWidget);
  });
}
```
Run: `flutter test integration_test` (device or emulator selected via `-d`). For web use `flutter drive` with `test_driver/integration_test.dart` calling `integrationDriver()` and chromedriver on port 4444.

Feedback loop on failures:
- `PumpAndSettleTimedOutException` -> an infinite animation is running; pump fixed durations.
- Widget not found -> it is lazily built; `scrollUntilVisible` first.
- Flaky -> replace `Future.delayed` waits with pumping until a finder matches; stub the backend.

## Running

```bash
flutter test                                  # all unit + widget tests
flutter test test/data/user_repository_test.dart
flutter test --coverage                       # lcov at coverage/lcov.info
flutter test --name "maps API model"          # filter by name
flutter analyze                               # must be clean before claiming done
```
