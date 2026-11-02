# Specs: Skill `antigravity-ops`

## 1. Skill Frontmatter & Metadata
- **Path**: `skills/antigravity-ops/SKILL.md`
- **Name**: `antigravity-ops`
- **Description**: `Use when installing, setting up, checking versions, or safely auto-updating Google Antigravity (standalone IDE & agy CLI) on Linux. Detects distro, architecture, libc, and the actual install method (tarball, dpkg/rpm/pacman, Snap, Flatpak, AppImage) before changing anything, and flags that Google's old APT/RPM repositories for Antigravity 1.x are historical and unsupported for current releases. Triggers on: antigravity, agy, update antigravity, setup antigravity, upgrade antigravity.`
- **Category**: `tech`
- **allowed-tools**: `Read, Write, Edit, Glob, Grep, Bash`

## 2. Verified facts and how to re-check them
| Claim | Verification command | Last confirmed |
|---|---|---|
| Linux standalone build ships a stub OTA updater | `grep -o '"updateUrl": "[^"]*"' <install-dir>/resources/app/product.json` → `"https://example.com"` | on a live install |
| `us-central1-apt.pkg.dev/projects/antigravity-auto-updater-dev` is frozen on `1.x` | `apt-cache policy antigravity`, compare `Candidate:` to the releases feed | `Candidate: 1.23.2` |
| Current-release feed (undocumented) | `curl -s https://antigravity-ide-auto-updater-974169037036.us-central1.run.app/releases` | returned `2.6.0` as newest |
| Tarball CDN URL shape (undocumented) | `curl -I "https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/<version>-<execution_id>/linux-x64/Antigravity%20IDE.tar.gz"` | `HTTP/2 200`, `content-length: 195292315`, `server: Google-Edge-Cache` |
| `linux-arm64` not published on that CDN path | same URL with `linux-arm64` | `HTTP/2 404` |

These are undocumented/unofficial endpoints with no stated SLA. Re-run the commands above before relying on a cached answer — don't just trust this table.

## 3. Decision-Tree Specification (Linux)
1. **A. Official standalone tarball / unpacked binary** (current recommended Google path):
   - Verify architecture (`x86_64` → Linux x64, `aarch64`/`arm64` → Linux ARM64) and minimums glibc >= 2.28, GLIBCXX >= 3.4.25.
   - Locate exactly one existing user `settings.json`; only then offer `set_update_mode.py --mode default`.
   - Desktop/PATH integration: write/repair `~/.local/share/applications/antigravity.desktop`, an icon under `~/.local/share/icons/hicolor/512x512/apps/` or `/usr/share/pixmaps/`, and a `~/.local/bin/antigravity` symlink; state the exact path before writing any of them.
   - In-place upgrade: query the releases feed → download the matching `linux-x64` tarball → extract to a staging dir → **confirm `pgrep -f antigravity` is empty** → `rsync --exclude=chrome-sandbox` into the install dir (preserves the existing SUID `chrome-sandbox`) → ask the user to relaunch.
2. **B. Package-managed (dpkg/rpm/pacman)**:
   - Report the owning package/manager. If it's the frozen `us-central1-apt.pkg.dev/projects/antigravity-auto-updater-dev` repo, warn that `apt-get upgrade` will not reach the current `2.x` line and offer the tarball path instead.
3. **C. Snap or Flatpak**:
   - Report the exact Snap name / Flatpak app ID and remote. Treat the package manager as the update authority; do not silently add remotes or switch formats.
4. **D. AppImage / custom wrapper / unknown**:
   - Report the path and ask how it was installed. Do not replace files or set up a downloader.
5. **E. macOS / Windows / WSL**:
   - Out of scope for this skill's scripts (Linux-only inspector). Point to https://antigravity.google/releases and the in-app Settings UI instead of fabricating platform-specific commands.

## 4. Automation Scripts
### `skills/antigravity-ops/scripts/inspect_environment.py`
- Python 3 standard library only, Linux-only (exits with `supported: false` on other platforms).
- Read-only: no sudo, no network calls, no writes.
- Reports: `/etc/os-release` fields, kernel, architecture + Google asset mapping, glibc/GLIBCXX versions and whether they meet Google's minimums, desktop session info, systemd-user availability, available package managers, Flatpak/Snap Antigravity packages, detected `install` type, running Antigravity processes, desktop entries, existing `settings.json` files with their current `update.mode`, and any legacy Antigravity repo config files found.
- `--json` emits the full report as JSON.

### `skills/antigravity-ops/scripts/set_update_mode.py`
- Edits the top-level `"update.mode"` key in **one existing** JSONC `settings.json`, passed via `--settings-file` (required) and `--mode` (`default`/`manual`/`none`, default `default`).
- Refuses to edit a file not owned by the current user (UID check).
- Always writes a timestamped `.bak.<timestamp>` backup (preserving file mode) before any change; writes the new content atomically via a temp file + `os.replace`.
- No-ops (prints a message, exits 0) if the file already has the requested mode.

## 5. Known issue: profile-directory split after a major update
Enabling `update.mode: default` does not by itself make the Linux standalone build auto-update (its `updateUrl` is a stub — see the table above). But if an update *is* applied (e.g. via the manual tarball flow, or a packaged build that does update), users have reported Antigravity splitting its profile directory across versions (e.g. `~/.config/Antigravity/User/` vs `~/.config/Antigravity IDE/User/`), which looks like a forced re-login / lost settings. This is community-reported, not confirmed in official docs:
- [Google antigravity 2 update broke setups](https://inventivehq.com/blog/google-antigravity-2-update-broke-setups)
- [Fix for Antigravity 2.0 hijacking the IDE, and how to restore your lost settings/extensions (Windows)](https://discuss.ai.google.dev/t/fix-for-antigravity-2-0-hijacking-the-ide-and-how-to-restore-your-lost-settings-extensions-for-windows-user/146158)

When `inspect_environment.py` reports more than one `settings_files` entry, treat it as a possible profile split, not an ambiguity to silently resolve: tell the user both paths and their `update_mode`, and do not assume data was lost — the old profile directory is typically still intact, just not read by the newer build. Re-login after a major version bump is expected; it is not evidence that `set_update_mode.py` (which only ever edits one key in one file) caused data loss.

## 6. Quality & Compliance
- Pass `python3 scripts/skill_lint.py`.
- Trigger cases in `tests/skills/trigger_cases.json` (`update antigravity`, `setup antigravity environment`, `how to upgrade antigravity ide`) pass `python3 scripts/trigger_test.py`.
- Pass `python3 scripts/skill_contract.py`.
- Re-generate `registry.min.json` via `make registry` and verify sync across `~/.gemini`, `~/.claude`, and `~/.codex` (`make install`).
- Refresh `docs/ai/manifest.json` checksums via `tools/memory_stale.py` after registry changes.
