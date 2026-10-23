# Proposal: Flutter Best-Practices Skills

Source: `docs/discovery/DISCOVERY-flutter-skills.md` (analysis of `references/flutter-agent-skill` and `references/agent-plugins`).

## 1. Context & Motivation
`prompt_base` has no Flutter-specific skill. `mobile-design` covers UX/platform conventions (with one `performance-flutter.md`), and `mobile-developer` lists Flutter but has nothing to load. The discovery report recommends one macro-skill with JIT references instead of importing Google's 25 micro-skills.

## 2. Key Decisions
- **One macro-skill** `flutter-best-practices`: lean `SKILL.md` (decision tables, rules, verify checklist) plus six references loaded on demand.
- **State management**: decision tree; **Riverpod is the default** when the user has no constraint. Google's MVVM (View / ViewModel / Repository / Service) defines the layering, Riverpod `Notifier`/`AsyncNotifier` plays the ViewModel role. BLoC and `ChangeNotifier` stay documented as alternatives.
- **Scope** (user choice): layout, state, testing, performance, plus `routing-and-data.md` and `dart-modern.md`. Flame 2D games become a **separate skill** `flutter-flame-games`, not folded into the main one.
- **Overlap with `mobile-design`**: leave it untouched; cross-link only.
- **Language**: English, same as existing skills. Adopt Google's *Task Progress* checklists with a feedback loop, and the layout error-signature table.
- **Corrections to sources**: the community skill uses legacy `StateProvider`/`StateNotifier` (moved to `legacy.dart` in Riverpod 3) and `withOpacity`; new skill uses current APIs and tells the agent to check the project's pinned versions first.

## 3. Out of Scope
- Firebase, platform channels, CI/CD, animation recipes (present in the source, not in the report's priorities).
- Generator CLI from `agent-plugins` (report ranks it L5, not an action item).
- Changes to `mobile-design`.

## 4. Risks
| Risk | Mitigation |
|---|---|
| Trigger collisions with `mobile-design` (`flutter`) | Distinct triggers (`dart`, `riverpod`, `widget`, `go_router`); run `make skill-check` and add trigger cases |
| API drift (Riverpod 3, Flame 1.x) | Skill instructs agent to read `pubspec.yaml` versions before applying snippets |
| Body over 300 lines fails lint | Keep `SKILL.md` lean, push detail into `references/` |
