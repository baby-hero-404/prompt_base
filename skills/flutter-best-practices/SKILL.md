---
name: flutter-best-practices
description: "Use when building, refactoring, or reviewing Flutter/Dart apps: widget layout and constraint errors, Riverpod/BLoC state, go_router navigation, performance, and widget/integration testing. Triggers on flutter, dart, riverpod, bloc, go_router, widget test, renderflex, pubspec."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
references: [layout-and-constraints.md, state-management.md, testing.md, performance-optimization.md, routing-and-data.md, dart-modern.md]
---

# Flutter Best Practices

> **Philosophy:** Constraints go down, sizes go up, parent sets position. UI is a pure function of state. `build()` stays cheap and side-effect free.
> **Scope:** code-level Flutter/Dart. For touch UX, platform look and feel, see the mobile-design skill. For 2D games, see the flutter-flame-games skill.

---

## Step 0: Read the project first (MANDATORY)

Snippets here assume a current stable SDK. Before writing code:
1. Read `pubspec.yaml`: SDK constraint, state package (`flutter_riverpod`, `flutter_bloc`, `provider`), router, test packages.
2. Check `analysis_options.yaml` and the existing folder layout. **Follow what the project already uses**; apply the defaults below only for new code or when the user has no preference.
3. If a snippet fails analysis, the package major version differs. Check the package changelog instead of guessing.

## Selective Loading Rule

Load ONLY the reference that matches the current task.

| Task | Load |
|---|---|
| `RenderFlex overflowed`, unbounded height/width, `ParentData` error, responsive or large-screen layout | `references/layout-and-constraints.md` |
| Choosing or implementing state management (Riverpod, BLoC, ChangeNotifier) | `references/state-management.md` |
| Writing unit, widget, golden, or integration tests | `references/testing.md` |
| Jank, rebuild storms, memory leaks, large lists, isolates, DevTools | `references/performance-optimization.md` |
| go_router, deep links, auth redirect, HTTP, JSON models, localization | `references/routing-and-data.md` |
| Records, patterns, sealed classes, primary constructors, Dart 3 idioms | `references/dart-modern.md` |

## Architecture (UI / Data, optional Domain)

Layers follow Google's MVVM guidance. Dependencies point inward: View -> ViewModel -> Repository -> Service.

| Layer | Responsibility | Rules |
|---|---|---|
| **View** (widget) | Render state, forward user events | No business logic, no I/O. Layout and animation only |
| **ViewModel** (Notifier / Cubit / `ChangeNotifier`) | Hold UI state, expose commands | Receives repositories by constructor/provider. Exposes immutable state |
| **Repository** | Single source of truth per data type | Maps API models to domain models; owns caching, retry, offline |
| **Service** | Stateless wrapper over HTTP, DB, platform plugin | Returns raw models or a `Result`. No UI knowledge |
| **Use case** (optional) | Logic shared by several ViewModels | Add only when a ViewModel gets cluttered |

Suggested layout (UI grouped by feature, data and domain grouped by type):

```text
lib/
├── data/{models,repositories,services}
├── domain/{models,use_cases}      # use_cases only if needed
└── ui/{core,features/<feature>/{view_models,views}}
```

## State Management Quick Choice

| Need | Use |
|---|---|
| Ephemeral, one widget (toggle, tab, animation) | `StatefulWidget` + `setState`, or `ValueNotifier` |
| Shared or async state, **no project preference** | **Riverpod** `Notifier` / `AsyncNotifier` / `StreamProvider` |
| Strict event -> state flows, audit trail, large team already on it | BLoC / Cubit |
| Small app, Google-style MVVM, fewest dependencies | `ChangeNotifier` + `ListenableBuilder` |

Never mix two global state solutions in one feature. Details and code in `references/state-management.md`.

## Hard Rules

| ID | Rule |
|---|---|
| F1 | **`build()` is pure and fast.** No HTTP, no controller creation, no parsing, no `setState`/`notifyListeners` calls inside it. It can run many times per second |
| F2 | **Dispose what you create.** `TextEditingController`, `ScrollController`, `AnimationController`, `FocusNode`, `StreamSubscription`, `Timer` get `dispose()`/`cancel()` in `dispose()` |
| F3 | **Guard async gaps.** After an `await` use `if (!mounted) return;` (State) or `if (!context.mounted) return;` before touching `context` or `setState` |
| F4 | **Fix layout at the cause.** Read the first exception, not the cascading `RenderBox was not laid out`. Do not hide overflow with `SingleChildScrollView` |
| F5 | **Lazy lists.** `ListView.builder` / `GridView.builder` / slivers for long or unknown-length lists. Never `shrinkWrap: true` on a long list |
| F6 | **`const` by default** for widgets and constructors that can be const. Turn on `prefer_const_constructors` |
| F7 | **Heavy work off the UI isolate.** JSON larger than ~16 ms parse time, crypto, image processing go through `compute()` or `Isolate.run()` |
| F8 | **Responsive by window, not by device.** `LayoutBuilder` / `MediaQuery.sizeOf`; no phone-vs-tablet checks, no orientation locks |
| F9 | **Throw on HTTP failure.** Never return `null` for a failed request; surface an error state in the UI |
| F10 | **Use current APIs.** `Color.withValues(alpha:)` not `withOpacity`, `PopScope` not `WillPopScope`, `MediaQuery.sizeOf(context)` not `MediaQuery.of(context).size` |

## Anti-Patterns

- Wrapping everything in `SingleChildScrollView` or `Expanded` until the red stripes disappear.
- A god `StatefulWidget` that fetches, parses, and renders.
- `setState` for app-wide state; passing state through five constructors instead of a provider.
- Creating `Future`/`Stream` inside `build()` (`FutureBuilder(future: fetch())` refetches on every rebuild). Create it in `initState` or a provider.
- Reading `ref.read` in `build()` for values the UI depends on (use `ref.watch`), or `ref.watch` inside callbacks (use `ref.read`).
- Business logic in widgets that cannot be tested without pumping a tree.
- Adding a package for something the SDK already does. Ask before adding dependencies.

## Task Progress (copy and track)

For any new feature:
- [ ] Read `pubspec.yaml` and existing structure (Step 0)
- [ ] Define domain models (immutable; `freezed` or hand-written with `copyWith`)
- [ ] Service -> Repository (map to domain models, throw on failure)
- [ ] ViewModel/Notifier with immutable state and command methods
- [ ] View: dumb widgets, `const` where possible, keys on list items that reorder
- [ ] Register route and dependencies
- [ ] Tests: ViewModel/repository unit tests first, then a widget test for the screen
- [ ] **Validator loop:** `dart format .` -> `flutter analyze` -> `flutter test` -> fix -> re-run until clean
- [ ] Run on a small and a large window size; confirm no overflow stripes in debug

## Cross-References

- `references/layout-and-constraints.md` for the error-signature table.
- mobile-design skill for touch targets, platform conventions, and its Flutter performance notes.
- mobile-developer agent for end-to-end mobile delivery.
- testing-patterns skill for generic test structure and mocking strategy.
