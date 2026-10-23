# Check Recipes

Language-neutral patterns. Implement with the project's own test runner. Exclude generated files (for example `*.g.dart`, `*.freezed.dart`, `*_pb.go`, `lib/l10n/*`) via an explicit list in the check, not by loosening the rule.

| Rule kind | Check | Failure message must include |
|---|---|---|
| Line limit (UI <= 300, other <= 400) | Walk source tree, count lines per file, classify UI by path | rule ID, file, line count, limit |
| Banned pattern (`Widget _build[A-Z]`, `Color(0x`, `print(`) | Regex over source, skip theme/allowlisted files | rule ID, file:line, matched text |
| Import boundary (`domain/` must not import framework/IO packages) | Parse import lines per layer directory, compare to forbidden list | rule ID, file:line, forbidden import |
| Cross-module isolation (`tools/zentao` must not import `tools/gitlab`) | Same as import boundary, sibling-to-sibling | rule ID, file:line, offending import |
| Required pairing (every `foo.go` has `foo_test.go`) | Walk tree, check counterpart exists | rule ID, missing file |

## Stack placement

| Stack | Where | Run via |
|---|---|---|
| Dart / Flutter | `test/architecture/architecture_rules_test.dart` (pure `dart:io` + `package:test`) | `flutter test`, included in `make verify` |
| Python | `tests/architecture/test_rules.py` (`unittest`, stdlib) | `python3 -m unittest`, included in `make verify` |
| Go | `*_test.go` using `go/parser` for imports, or a `go vet` analyzer | `go test ./...` |
| TypeScript | `eslint` `no-restricted-imports` / `max-lines`, else a small node test | `npm run lint` / `npm test` |

Prefer the linter's built-in rule (`max-lines`, `no-restricted-imports`) when one exists; write a custom test only for what the linter cannot express.

## Skeleton (Python, stdlib)

```python
import re, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXCLUDE = ("generated",)

def source_files(suffix):
    return [p for p in ROOT.rglob(f"*{suffix}") if not any(x in p.parts for x in EXCLUDE)]

class ArchitectureRules(unittest.TestCase):
    def test_6_1_ui_file_line_limit(self):
        bad = [f"6.1 {p} has {n} lines (max 300)" for p in source_files(".py")
               if "ui" in p.parts and (n := len(p.read_text().splitlines())) > 300]
        self.assertEqual(bad, [], "\n".join(bad))
```
