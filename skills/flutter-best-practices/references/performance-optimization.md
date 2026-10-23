# Performance Optimization

Frame budget: 16 ms at 60 Hz, 8 ms at 120 Hz, for **both** the UI thread (build/layout) and the raster thread. **Measure before and after** in profile mode on a real device; debug mode numbers are meaningless.

```bash
flutter run --profile        # never judge performance in debug
```

## 1. Keep `build()` Cheap

`build()` can be called every frame during animation. Inside it, do not:
- create controllers, `Future`s, `Stream`s, or subscriptions
- fetch, parse JSON, sort or filter big collections
- call `setState` / `notifyListeners`

```dart
// BAD: refetches on every rebuild
FutureBuilder(future: repo.load(), builder: ...)

// GOOD: created once
late final Future<Data> _future = repo.load();      // in State
FutureBuilder(future: _future, builder: ...)        // or a Riverpod/Bloc provider
```

## 2. Reduce Rebuild Scope

| Technique | Use |
|---|---|
| `const` widgets and constructors | Skips rebuilding unchanged subtrees. Enable lints `prefer_const_constructors`, `prefer_const_literals_to_create_immutables` |
| Extract a `StatelessWidget` class (not a helper method) | Gives Flutter an element boundary it can skip; methods rebuild with the parent |
| Push state down | Put `setState` / `watch` in the smallest subtree that changes |
| `select` / `buildWhen` / `BlocSelector` | Rebuild only when the used field changes |
| `ValueNotifier` + `ValueListenableBuilder` | Local state without rebuilding the whole widget |
| Pass `child` to `AnimatedBuilder` / `ListenableBuilder` | Static subtree is built once |
| Stable `Key`s in reorderable lists | Preserves element state on reorder |

## 3. Lists and Scrolling

- `ListView.builder` / `GridView.builder` / `SliverList.builder` for long lists. Never `children: items.map(...).toList()` on large data.
- Supply `itemExtent` / `prototypeItem` for uniform rows to skip layout measuring.
- Avoid `shrinkWrap: true` and nested scrollables of the same axis; use `CustomScrollView` with slivers.
- Page network data (infinite scroll); do not load everything.
- Keep `itemBuilder` light; precompute display strings in the view model.

## 4. Images

- Use `cacheWidth`/`cacheHeight` (or `ResizeImage`) so decoded size matches display size.
- Use `cached_network_image` or equivalent for network images; prefer WebP/AVIF assets.
- Limit the global cache on constrained devices:
```dart
PaintingBinding.instance.imageCache
  ..maximumSize = 100
  ..maximumSizeBytes = 50 << 20;   // 50 MB
```

## 5. Repaint and Compositing

- Wrap frequently animating, independent subtrees in `RepaintBoundary` (verify benefit with the repaint rainbow; overuse costs memory).
- Avoid `Opacity` on large subtrees (use `AnimatedOpacity`/`FadeTransition` or paint colour with alpha), avoid unnecessary `ClipRRect`/`ClipPath` and `saveLayer` triggers (`ShaderMask`, `BackdropFilter`, big shadows).
- Prefer implicit/explicit animation widgets over rebuilding with timers.

## 6. Memory and Lifecycle (Leak Prevention)

```dart
class _FeedState extends State<Feed> {
  final _scroll = ScrollController();
  late final StreamSubscription<Event> _sub;

  @override
  void initState() {
    super.initState();
    _sub = events.listen(_onEvent);
  }

  Future<void> _refresh() async {
    final data = await repo.load();
    if (!mounted) return;               // CRITICAL after any await
    setState(() => _data = data);
  }

  @override
  void dispose() {
    _sub.cancel();
    _scroll.dispose();
    super.dispose();                    // call super.dispose() last
  }
}
```

Dispose list: `TextEditingController`, `ScrollController`, `PageController`, `TabController`, `AnimationController`, `FocusNode`, `StreamSubscription`, `Timer`, `ChangeNotifier`/`ValueNotifier` you created, `StreamController`. Use `SingleTickerProviderStateMixin` for one `AnimationController`.

After an `await` in a non-State context (callbacks, services) use `if (!context.mounted) return;` before using `context`.

## 7. Heavy Work Off the UI Isolate

Anything over about one frame (~16 ms): large JSON parse, image decode/resize, crypto, compression, big sorting.

```dart
// Flutter helper, works on all platforms
final models = await compute(parseModels, responseBody);   // parseModels: top-level or static

// Dart 3, preferred where available (not on web)
final result = await Isolate.run(() => heavy(input));

// Top-level function: closures capturing non-sendable objects will fail
List<Model> parseModels(String body) =>
    (jsonDecode(body) as List).cast<Map<String, dynamic>>().map(Model.fromJson).toList();
```

Rules: arguments and results must be sendable (primitives, lists, maps, records, simple classes). You cannot touch plugins or widgets from a plain isolate. For long-lived work use `Isolate.spawn` + ports, or a worker package. Do not spawn isolates for small payloads; the copy cost outweighs the gain.

## 8. Startup and Size

- Defer heavy init until after the first frame (`WidgetsBinding.instance.addPostFrameCallback`) or show a splash.
- Lazy-load rarely used screens; on web use deferred imports (`import '...' deferred as x`).
- `flutter build apk --split-per-abi`, `--obfuscate --split-debug-info=build/symbols` for release, and tree shake icons (default in release).
- Audit dependencies: each package adds startup and binary size.

## 9. Profiling Workflow (Task Progress)

- [ ] Run in **profile** mode on a mid/low-end physical device.
- [ ] Open DevTools -> Performance; enable "Track widget builds" and look for red frames.
- [ ] UI thread slow -> reduce rebuilds (section 2), move work to an isolate (7).
- [ ] Raster thread slow -> check `saveLayer`, clipping, large images, shaders (5, 4). Use Impeller defaults; capture shader jank only if you see first-run hitching.
- [ ] Memory tab: take snapshots before/after navigating a screen 10 times; growth means a leak (section 6).
- [ ] Timeline "Rebuild Counts": find widgets rebuilding without need.
- [ ] Apply one change at a time, re-measure, keep only what helps.
- [ ] Debug helpers (temporary only): `debugRepaintRainbowEnabled = true;`, `debugPrintRebuildDirtyWidgets = true;`.

## Quick Priority Table

| Rule | Priority |
|---|---|
| No work in `build()` | Critical |
| Builders for long lists | Critical |
| Dispose controllers and cancel subscriptions | Critical |
| `mounted` check after await | Critical |
| `const` constructors | High |
| Isolates for heavy parsing | High |
| Resized images and bounded cache | High |
| `RepaintBoundary`, avoid clip/opacity abuse | Medium |
