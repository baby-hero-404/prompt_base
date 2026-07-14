#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────
# Prompt Base — Post-Install Cleanup
# Removes development-only files after cloning into ~/.gemini
# 
# Usage:
#   bash ~/.gemini/scripts/cleanup.sh          (auto-detect)
#   bash scripts/cleanup.sh /path/to/root      (explicit root)
# ─────────────────────────────────────────────────────────

set -uo pipefail

# Resolve root directory
ROOT="${1:-$(cd "$(dirname "$0")/.." && pwd)}"

echo "🧹 Prompt Base — Post-Install Cleanup"
echo "📁 Root: $ROOT"
echo ""

# ── Verify this is actually a Prompt Base installation ──
if [[ ! -f "$ROOT/GEMINI.md" && ! -f "$ROOT/CLAUDE.md" ]] || [[ ! -f "$ROOT/registry.min.json" ]]; then
    echo "❌ Error: $ROOT does not look like a Prompt Base installation."
    echo "   Missing GEMINI.md, CLAUDE.md, or registry.min.json"
    exit 1
fi

# ── Files & directories to remove ──
# These are development-only and NOT needed at runtime.

removed=0
skipped=0

# ── Clean any __pycache__ directories ──
pycache_count=$(find "$ROOT" -type d -name "__pycache__" 2>/dev/null | wc -l)
if [[ "$pycache_count" -gt 0 ]]; then
    find "$ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    echo "  🗑️  Removed: $pycache_count __pycache__ dir(s)"
fi



# ── Summary ──
echo ""
echo "✅ Cleanup complete!"
echo "   Removed: $removed items"
echo "   Skipped: $skipped (not found)"
echo ""
echo "📦 Remaining (runtime essentials):"
echo "   GEMINI.md / CLAUDE.md  ← Rules (always active)"
echo "   ARCHITECTURE.md        ← System map"
echo "   registry.min.json      ← Skill discovery"
echo "   core/                  ← Core logic"
echo "   tools/                 ← Agent utilities"
echo "   antigravity/agents/    ← Agent definitions"
echo "   antigravity/skills/    ← Skills (auto-trigger)"
echo "   antigravity/global_workflows/  ← Workflows (slash commands)"
