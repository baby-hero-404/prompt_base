"""Shared by the hook installers: spot hook commands left over from before the
shared runtime moved to ~/.agents.

~/.claude/tools and ~/.gemini/tools are now symlinks to ~/.agents/tools, so an old
entry pointing there runs the very same script as its ~/.agents twin and every
event fires it twice.
"""

LEGACY_PREFIXES = (
    ("$HOME/.claude/venv", "$HOME/.agents/venv"),
    ("$HOME/.claude/tools", "$HOME/.agents/tools"),
    ("$HOME/.gemini/venv", "$HOME/.agents/venv"),
    ("$HOME/.gemini/tools", "$HOME/.agents/tools"),
)


def agents_twin(command):
    """The ~/.agents form of a legacy command, or None if it is not legacy."""
    if not isinstance(command, str):
        return None
    twin = command
    for old, new in LEGACY_PREFIXES:
        twin = twin.replace(old, new)
    return twin if twin != command else None


def prune_legacy_duplicates(handlers):
    """Drop handlers whose ~/.agents twin is also present. Returns a new list."""
    commands = {h.get("command") for h in handlers if isinstance(h, dict)}
    return [
        h for h in handlers
        if not (isinstance(h, dict) and agents_twin(h.get("command")) in commands)
    ]
