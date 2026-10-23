# Tasks: Memory Management Refresh

Order: M2 -> M3 (tests first) -> M1 -> M4 -> verification.

- [x] **M2: Staleness check** (`docs/ai/manifest.json`)
  - [x] Tests `tools/tests/test_memory_stale.py`: fresh, stale after edit, new trigger file, missing manifest, missing trigger file ignored, `--update` roundtrip.
  - [x] `tools/memory_stale.py` (stdlib): `--root <path> [--update]`; exit 1 when stale.
  - [x] Wire into `global_workflows/init-context.md` (`--update`) and `global_workflows/status.md` (check).

- [x] **M3: Invariant re-injection**
  - [x] Tests `tools/tests/test_memory_invariants.py`: no DOMAIN file, no invariants section, legacy fallback path, 1500-char cap, secret skip, 1st and every 10th prompt, malformed stdin, CLI mode.
  - [x] `tools/memory_invariants.py` (stdlib): `print` CLI (any agent) and hook mode (stdin JSON, Claude). Exit 0 always.
  - [x] Register in `settings.json` under `UserPromptSubmit`; extend `test_install_settings.py`.
  - [x] Rule line for agents without hooks in `GEMINI.md` / `CLAUDE.md` context hygiene: read invariants at session start and every ~10 turns, tagged `[review]`.

- [x] **M1: Unified memory model (docs)**
  - [x] `skills/project-memory/SKILL.md`: "Memory layers" table with agent-neutral column; `docs/ai/` canonical (`PROFILE.md`, `DOMAIN.md`, `manifest.json`, `adr/`, `archive/`).
  - [x] `references/extended-reference.md`: mark old `AI_PROJECT_CONTEXT` / `PROJECT_INDEX` / `CODING_PATTERNS` files superseded by `PROFILE`/`DOMAIN`.
  - [x] `global_workflows/init-context.md`: write to `docs/ai/` (ask before writing into the project repo), legacy `~/.gemini/projects/` as read fallback, templates from `projects/_template/`.
  - [x] Migrate this repo: copy `~/.gemini/projects/my_projects-prompt_base/*` to `docs/ai/`.
  - [x] Sync `ARCHITECTURE.md`, `skills/context-management/SKILL.md`, `CLAUDE.md` / `GEMINI.md` context-hygiene line.

- [x] **M4: Operations**
  - [x] `tools/memory_status.py` + `make memory-status` (read-only): memory dir, rows by kind, FTS vs vec mode, last recall, sibling DB dirs for the same project name.
  - [x] Run `make memory-setup` (confirmed by user).
  - [x] List duplicate prompt_base DB dir and delete only after user confirms the path (deleted `prompt_base-76630424942b1d60`, 0 rows).

- [x] **M5: Opt-in per project**
  - [x] Tests `tools/tests/test_memory_optin.py` (hooks write nothing unless `docs/ai/` exists and project trusted) + `pb_trust --remove` tests.
  - [x] `pb_trust.memory_enabled`, `pb_trust --remove`; gate `memory_compact.py` and `memory_recall.py` in `main()`.
  - [x] `global_workflows/init-memory.md`; `/init-context` reduced to read-only.
  - [x] Docs: `README.md`, `ARCHITECTURE.md`, `CLAUDE.md` / `GEMINI.md`, `project-memory` skill, `status.md`, tool messages.
  - [ ] `make install` to publish (user).

- [ ] **Verification**
  - [x] `make test`, each `tools/tests/test_*.py`, `make skill-check`, `make registry`.
  - [x] Dry-run `install_settings.py` against a temp settings copy (idempotent merge).
  - [ ] `make install` only after user confirms.
