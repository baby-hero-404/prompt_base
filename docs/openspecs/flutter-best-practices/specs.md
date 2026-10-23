# Specification: Flutter Skills

## 1. Deliverables
```
skills/flutter-best-practices/
├── SKILL.md                         # body <= 150 lines
└── references/
    ├── layout-and-constraints.md    # error signatures, responsive, anti-patterns
    ├── state-management.md          # decision tree, Riverpod, BLoC, ChangeNotifier
    ├── testing.md                   # unit, widget, golden, integration
    ├── performance-optimization.md  # build(), const, lists, disposal, isolates, DevTools
    ├── routing-and-data.md          # go_router, http, JSON, l10n
    └── dart-modern.md               # records, patterns, sealed, primary constructors
skills/flutter-flame-games/
├── SKILL.md
└── references/
    ├── collision-and-input.md
    └── camera-tiled-audio.md
agents/mobile-developer.md           # link skills, add triggers and Flutter verify checklist
registry.min.json                    # via `make registry`
tests/skills/trigger_cases.json      # new cases for both skills
```

## 2. SKILL.md Contract (`flutter-best-practices`)
- Frontmatter: `name`, `description` ("Use when ... Triggers on ..."), `allowed-tools` limited to known tools, `references` list.
- Sections: selective-loading table, architecture layering, state decision table, hard rules, anti-patterns, Task Progress verify checklist.
- Every reference listed in the loading table exists; every backticked path resolves (`skill_contract.py`).

## 3. Behaviour Requirements
| ID | Requirement |
|---|---|
| F1 | MUST tell the agent to read `pubspec.yaml` (Flutter/Dart/package versions) before applying snippets |
| F2 | MUST NOT put side effects, controllers, HTTP or heavy parsing in `build()` |
| F3 | MUST fix layout errors from the primary exception, not by wrapping in `SingleChildScrollView` |
| F4 | MUST dispose controllers/subscriptions and guard async `setState` with `mounted` |
| F5 | MUST default to Riverpod only when the project has no existing state solution; otherwise follow the project |
| F6 | MUST use builders for long lists and `compute()`/`Isolate.run` for parsing > ~16 ms |
| F7 | Verify checklist MUST include `flutter analyze` and `flutter test` |

## 4. Acceptance
- `make skill-check` passes (lint, trigger test, contract).
- `make registry` lists both skills; `make install` deploys them.
- Trigger cases: Flutter widget/layout prompt -> `flutter-best-practices`; Flame game prompt -> `flutter-flame-games`.
- `make verify`/`make test` unchanged or passing.
