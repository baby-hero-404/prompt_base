# State Management

First rule: **follow the state solution already in `pubspec.yaml`.** The defaults below apply to new projects or when the user has no preference.

## Decision Tree

1. Is the state used by exactly one widget and dies with it (toggle, tab index, text focus, animation)? -> `StatefulWidget` + `setState`, or a `ValueNotifier` with `ValueListenableBuilder`.
2. Is it shared, async (API, DB, cache) or must survive navigation? -> go to 3.
3. Does the project already use a solution? -> use it.
4. No preference:
   - Default: **Riverpod** (`Notifier`, `AsyncNotifier`, `StreamNotifier`, plain `Provider`).
   - Event-driven, explicit transitions, replayable, team already knows BLoC: **BLoC / Cubit**.
   - Tiny app, want zero state packages (Google MVVM sample style): **`ChangeNotifier`** + `ListenableBuilder`.

| State kind | Riverpod | BLoC | ChangeNotifier |
|---|---|---|---|
| Local ephemeral | `setState` | `setState` | `setState` |
| Sync shared value | `Notifier` | Cubit | `ChangeNotifier` |
| Async load / mutation | `AsyncNotifier` | Bloc with load events | ViewModel with `isLoading` + error |
| Live stream | `StreamProvider` / `StreamNotifier` | `emit.forEach` | `StreamSubscription` in ViewModel (cancel on dispose) |
| Derived data | `Provider` that `watch`es others | Selector / separate Bloc | getter |
| Dependency injection | providers themselves | `RepositoryProvider` | `provider`/`get_it` |

Never run two global state solutions side by side inside one feature.

## Riverpod

### Version Check
Riverpod 3 moved `StateProvider`, `StateNotifierProvider` and `ChangeNotifierProvider` to `package:flutter_riverpod/legacy.dart`. **Prefer `Notifier`/`AsyncNotifier` for new code.** Annotation-based (`@riverpod` + `riverpod_generator`) is optional; only use it if the project already runs `build_runner`.

### Setup
```dart
void main() => runApp(const ProviderScope(child: MyApp()));
```

### Layering with Providers
```dart
// data layer
final apiClientProvider = Provider<ApiClient>((ref) => ApiClient());
final userRepositoryProvider = Provider<UserRepository>(
  (ref) => UserRepository(apiClient: ref.watch(apiClientProvider)),
);

// view model: async state with loading/error/data for free
class ProfileNotifier extends AsyncNotifier<User> {
  @override
  Future<User> build() => ref.watch(userRepositoryProvider).getCurrentUser();

  Future<void> rename(String name) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(
      () => ref.read(userRepositoryProvider).rename(name),
    );
  }
}
final profileProvider = AsyncNotifierProvider<ProfileNotifier, User>(ProfileNotifier.new);

// sync state
class CartNotifier extends Notifier<List<CartItem>> {
  @override
  List<CartItem> build() => const [];

  void add(CartItem item) => state = [...state, item];            // always a NEW list
  void remove(String id) => state = [for (final i in state) if (i.id != id) i];
}
final cartProvider = NotifierProvider<CartNotifier, List<CartItem>>(CartNotifier.new);
```

### Consuming
```dart
class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    ref.listen(profileProvider, (prev, next) {
      if (next.hasError && !next.isLoading) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Failed')));
      }
    });
    final profile = ref.watch(profileProvider);
    return profile.when(
      data: (u) => Text(u.name),
      loading: () => const CircularProgressIndicator(),
      error: (e, st) => ErrorView(error: e, onRetry: () => ref.invalidate(profileProvider)),
    );
  }
}
```

### Rules
| Rule | Why |
|---|---|
| `ref.watch` in `build` (and in provider bodies); `ref.read` in callbacks; `ref.listen` for side effects (snackbars, navigation) | Wrong verb gives stale UI or rebuild loops |
| Never `ref.read` inside `build` for data the UI shows | UI will not update |
| Update state immutably (`state = [...state, x]`, `copyWith`) | Mutation does not notify listeners |
| Narrow rebuilds: `ref.watch(p.select((s) => s.name))` | Rebuild only when the selected field changes |
| `autoDispose` (default with codegen/Riverpod 3 patterns) for screen-scoped state; `keepAlive` only for real caches | Prevents leaked state |
| Use `family` for parameterised providers (`userProvider(id)`) | One cache entry per argument |
| Do not use `BuildContext` inside a Notifier | Keeps logic testable |
| `AsyncValue.guard` around fallible calls | Captures errors into state rather than throwing |

### Testing Riverpod
```dart
test('cart adds item', () {
  final container = ProviderContainer(overrides: [
    userRepositoryProvider.overrideWithValue(FakeUserRepository()),
  ]);
  addTearDown(container.dispose);

  container.read(cartProvider.notifier).add(item);
  expect(container.read(cartProvider), [item]);
});

testWidgets('shows name', (tester) async {
  await tester.pumpWidget(ProviderScope(
    overrides: [profileProvider.overrideWith(() => FakeProfileNotifier())],
    child: const MaterialApp(home: ProfileScreen()),
  ));
  await tester.pumpAndSettle();
  expect(find.text('Ada'), findsOneWidget);
});
```

## BLoC / Cubit

Use a **Cubit** when state changes are simple method calls; use a **Bloc** when you need event transformers (debounce, `restartable`, `droppable`) or an event log.

```dart
sealed class CounterEvent {}
final class Incremented extends CounterEvent {}

class CounterState {
  const CounterState(this.count);
  final int count;
}

class CounterBloc extends Bloc<CounterEvent, CounterState> {
  CounterBloc() : super(const CounterState(0)) {
    on<Incremented>((event, emit) => emit(CounterState(state.count + 1)));
  }
}

// provide above the widgets that need it
BlocProvider(create: (_) => CounterBloc(), child: const CounterView());

// rebuild UI
BlocBuilder<CounterBloc, CounterState>(builder: (context, s) => Text('${s.count}'));
// side effects (navigation, snackbar)
BlocListener<CounterBloc, CounterState>(listener: (context, s) {/* ... */}, child: child);
// both
BlocConsumer<CounterBloc, CounterState>(listener: ..., builder: ...);
```

Rules:
- States are immutable and implement `==` (use `Equatable` or `freezed`), otherwise `emit` of an equal state still rebuilds.
- Model status with a sealed class (`Loading`, `Loaded`, `Failure`) rather than nullable fields and booleans.
- Inject repositories through the constructor; never reach for a singleton inside the Bloc.
- `context.read<B>()` in callbacks, `context.watch<B>()`/`BlocBuilder` in `build`. Use `buildWhen` / `BlocSelector` to limit rebuilds.
- Test with `bloc_test`: `blocTest(build: ..., act: ..., expect: () => [...])`.

## ChangeNotifier + ListenableBuilder (Google MVVM)

```dart
class ProfileViewModel extends ChangeNotifier {
  ProfileViewModel({required UserRepository userRepository}) : _repo = userRepository;
  final UserRepository _repo;

  User? _user;
  User? get user => _user;
  bool _loading = false;
  bool get loading => _loading;
  Object? _error;
  Object? get error => _error;

  Future<void> load(String id) async {
    _loading = true; _error = null;
    notifyListeners();
    try {
      _user = await _repo.getUser(id);
    } catch (e) {
      _error = e;
    } finally {
      _loading = false;
      notifyListeners();
    }
  }
}

ListenableBuilder(
  listenable: viewModel,
  builder: (context, _) => viewModel.loading ? const CircularProgressIndicator() : Text(viewModel.user?.name ?? ''),
);
```

Rules: create the ViewModel once (provider/`get_it`/`initState`, never in `build`), call `dispose()` on it, expose read-only getters, and never call `notifyListeners()` after dispose.

## Common Mistakes

- Creating the ViewModel/Bloc inside `build()` (recreated on every rebuild, state lost).
- Mutating a list/map in state and expecting a rebuild.
- Forgetting an error state: every async state has loading, data, **and** error.
- Putting navigation calls inside the notifier; emit a one-shot event/state and navigate from a `listen`/`BlocListener`.
- Global singletons holding mutable UI state, which makes tests order-dependent.
