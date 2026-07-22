---
name: context-management
description: "Use when optimizing the context window or implementing Minimal Viable Context (MVC) to prevent token bloat."
---
# Context Management Protocol
1. Prioritize current task files.
2. Summarize older conversation history.
3. Identify and remove redundant skill documentation once the goal is reached.
4. Maintain a "Minimal Viable Context" (MVC) at all times.

## Long-term compression/recall is hook-enforced, not just advisory
Compression at session boundaries and recall at session start are handled automatically by the context memory engine's `PreCompact`/`UserPromptSubmit` hooks when installed (see `project-memory`, Section 0) — they run regardless of whether the agent remembers to prune. Emit `<adr>` tags for decisions worth capturing long-term; don't manually re-summarize old history into a file for that purpose.

The Slot discipline above (and in `project-memory skill's memory rules`) remains the **documented fallback**: it's what governs in-session context hygiene always, and it's the only mechanism active if hooks are disabled or not installed for this project.

## Token-Efficient Output
To maintain MVC and reduce output tokens, compress stylistic filler (articles, pleasantries) but never actual words or language. 
**BPE-Tokenizer Rationale**: Do not invent new abbreviations (like `cfg` or `impl`) or use arrow chains (`->`). Modern BPE (Byte Pair Encoding) tokenizers split unrecognized abbreviations into multiple fragments. Thus, `impl` often costs the same or more tokens than `implementation`, but sacrifices human readability. Write the full technical word.
