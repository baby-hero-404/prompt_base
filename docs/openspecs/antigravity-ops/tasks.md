# Tasks: Skill `antigravity-ops`

- [x] **T1: Scaffold Skill (`skills/antigravity-ops/`)**
  - [x] Run `python3 scripts/create_skill.py antigravity-ops --description "..." --trigger-case "update antigravity"`.
  - [x] Verify directory creation and registry entry.
- [x] ~~T2: Implement Environment-Aware Manager Script (`antigravity_manager.py`)~~ **(superseded by T6 — removed)**
  - The first draft assumed a Google APT repo (`us-central1-apt.pkg.dev`) and Snap-based `agy` CLI. That script was deleted.
- [x] ~~T3: Author Comprehensive Skill Guide~~ **(superseded by T6, then T7 — rewritten twice)**
- [x] **T6: Replace with an inspect-first, Linux-only workflow**
  - [x] Verified Google's documented tarball distribution and the `update.mode` setting against https://antigravity.google/releases.
  - [x] Added `inspect_environment.py` (read-only Linux inspector) and `set_update_mode.py` (backup-first JSONC `update.mode` editor), replacing the APT/Snap script.
  - [x] Rewrote `SKILL.md` around a 5-way decision tree (tarball / package-managed / Snap-Flatpak / AppImage / macOS-Windows-out-of-scope).
- [x] **T7: Correct and harden the install-method claims (user-authored revision)**
  - [x] Discovered and confirmed, by inspecting a live install, that `product.json`'s `updateUrl` is a stub (`https://example.com`) — the in-app OTA updater does not function on Linux standalone builds.
  - [x] Discovered and confirmed, via `apt-cache policy antigravity`, that `us-central1-apt.pkg.dev/projects/antigravity-auto-updater-dev` is frozen at `1.23.2` — it does not track the current `2.x` line.
  - [x] Discovered and independently verified (via `curl`) an undocumented current-release feed (`.../releases`, returns `2.6.0` latest) and the matching CDN tarball URL shape (`edgedl.me.gvt1.com`, `HTTP/2 200`, `content-length: 195292315`); confirmed `linux-arm64` is not published there (404).
  - [x] Added a manual tarball in-place upgrade flow (query feed → download → stage → confirm no running process → `rsync` excluding `chrome-sandbox` → restart), with an explicit "app must be fully closed before `rsync`" safety gate.
  - [x] Added mandatory desktop-entry/icon/PATH-symlink setup for tarball installs.
  - [x] Added self-verification commands (`grep updateUrl`, `curl` the releases feed, `apt-cache policy`) directly into `SKILL.md` so future agents re-derive claims instead of trusting hardcoded text.
  - [x] Re-synced `docs/openspecs/antigravity-ops/{proposal,specs,tasks}.md` to the final state (this revision).
- [x] **T4: Testing & Quality Gates**
  - [x] Trigger cases present in `tests/skills/trigger_cases.json`.
  - [x] Run Tier 1 (`skill_lint.py`), Tier 2 (`trigger_test.py`), Tier 0 (`skill_contract.py`) — all pass.
  - [x] Run `make verify`.
- [x] **T5: Demonstrate & Check**
  - [x] Ran `inspect_environment.py --json` on a live machine — correctly reported an APT-installed `antigravity` package and its settings file.
  - [x] Confirmed sync to `~/.gemini/config/skills/`, `~/.codex/skills/`, and `~/.claude/skills/`, and that `registry.min.json` carries a matching entry.

## Open item for a future revision
- The "profile-directory split causes forced re-login" issue (see `specs.md` §5) is sourced from community forum/blog reports, not official Google docs. If Google publishes an official explanation, update that section's sourcing accordingly.
