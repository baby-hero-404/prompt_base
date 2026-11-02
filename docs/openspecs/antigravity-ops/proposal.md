# Proposal: Skill `antigravity-ops` (Environment-Aware Setup & Auto-Update)

## 1. Context & Motivation
Google Antigravity (the standalone Antigravity IDE and the Antigravity CLI `agy`) is the core execution platform for agentic pair-programming. Update guidance for it has shifted twice during this skill's development, so the skill now documents only claims that were independently verified against a running machine, not secondhand summaries:
1. An early draft assumed the IDE updates itself through a Google-hosted APT repo (`https://us-central1-apt.pkg.dev/projects/antigravity-auto-updater-dev`) and that `agy` is a Snap package.
2. Checking an actual installed Antigravity (`apt-cache policy antigravity`) showed that repo's `Candidate` stops at `1.23.2` — it never moved past the `1.x` line.
3. Querying Google's own (undocumented) releases feed, `https://antigravity-ide-auto-updater-974169037036.us-central1.run.app/releases`, returns the real current line (`2.6.0` and newer at time of writing) — confirming the APT repo is frozen on `1.x`, not actively tracking current releases.
4. The CDN download URL derived from that feed, `https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/<version>-<execution_id>/linux-x64/Antigravity%20IDE.tar.gz`, was independently verified with `curl -I`: `HTTP/2 200`, `content-length: 195292315`, served by Google's Edge Cache. The same URL with `linux-arm64` 404s — only `linux-x64` is currently published there.
5. `product.json` inside an installed Antigravity build contains `"updateUrl": "https://example.com"` — a stub — confirming the in-app OTA updater does not function for the Linux standalone build; `update.mode` only controls whether that (non-functional, on Linux) check runs, it does not make upgrades happen by itself.

## 2. Key Decisions
- **Skill Name & Category**: `antigravity-ops` in the `tech` category.
- **Verify, don't assume**: every factual claim in `SKILL.md` has a command next to it that re-derives the claim on the machine being used (`grep updateUrl product.json`, `curl` the releases feed, `apt-cache policy antigravity`). Undocumented/unofficial endpoints (the releases feed, the CDN path shape) are labeled as such — best-effort, no SLA, re-check before trusting.
- **Install-type decision tree** (Linux): (A) official tarball/unpacked binary — the recommended path, with its own in-place upgrade flow (query releases feed → download → stage → confirm app fully closed → `rsync` into place, excluding `chrome-sandbox` to preserve its SUID bit → restart); (B) package-managed (dpkg/rpm/pacman) — report the owner and warn if it's the frozen `1.x` APT repo; (C) Snap/Flatpak — treat the package manager as the update authority; (D) AppImage/unknown — report and ask, never replace; (E) macOS/Windows — out of scope for this skill's Linux-only scripts, point to official docs.
- **Safety gates**: never `rsync` into a running app's install directory (`pgrep -f antigravity` must be empty first); never force-kill Antigravity to force an update; never add/refresh the frozen `1.x` APT/RPM repo as if it were current; `set_update_mode.py` only ever edits one key in one existing, user-owned `settings.json`, always with a timestamped backup first.
- **Desktop/PATH integration**: standalone tarballs don't register a desktop entry or PATH symlink, so creating `~/.local/share/applications/antigravity.desktop`, an icon, and a `~/.local/bin/antigravity` symlink are treated as part of a correct tarball setup — done only after stating the exact files that will be written/changed.
- **Components Managed**:
  - **Antigravity IDE**: tarball install/upgrade via the verified releases feed + CDN, or the IDE's own `update.mode` setting; package-managed/Snap/Flatpak installs are inspected and reported, with their own manager treated as update authority.
  - **Antigravity CLI (`agy`)**: inspected/reported only; this skill does not manage its install or update path.
- **Automation Scripts**:
  - `skills/antigravity-ops/scripts/inspect_environment.py` — read-only, standard-library-only Linux inspector (no sudo, no network calls, no changes).
  - `skills/antigravity-ops/scripts/set_update_mode.py` — edits `update.mode` in one existing, detected JSONC `settings.json`, with a mandatory timestamped backup before any write.
