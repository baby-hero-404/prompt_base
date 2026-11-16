# Project Discovery Report — Cleanup Skills

> **Mục tiêu**: phân tích 4 nguồn (`revise-skill`, `pro-workflow`, `awesome-copilot`, `awesome-agent-skills`) để nâng cấp bộ skill dọn dẹp codebase trong `prompt_base`. Spec: [`docs/openspecs/cleanup-skills-enhance/`](../openspecs/cleanup-skills-enhance/). Mỗi nguồn được đọc riêng, rồi tổng hợp ở mục 6.

---

## 1. TL;DR

| Nguồn | Thực chất là gì | Giá trị cho cleanup |
|---|---|---|
| `revise-skill` | 1 skill + 57 "pattern" rút ra từ việc tác giả tự sửa tay code do AI viết | Cao về **phương pháp** (kiểm chứng trước khi xóa, hai lượt sửa, "When NOT to revise"); phần lớn pattern là style riêng Python/JS nên không lấy |
| `pro-workflow` | Plugin Claude Code lớn (40 skill, hook Node, MCP, wiki) | Lấy 3 thứ: `deslop` (danh sách AI slop), `improve-architecture`, rule `module-shape`; **không** lấy hook, script, plugin |
| `awesome-copilot` | Kho cộng đồng của GitHub: 229 agent, 463 skill, 195 instruction | Lấy ý từ ~8 file: `gem-code-simplifier`, `test-gap-audit`, `tech-debt-remediation-plan`, `reviewer`-style evidence rules. **Không có `cleanup-specialist`** như bạn ghi |
| `awesome-agent-skills` | Chỉ là **danh mục link** (README 2041 dòng, không có nội dung skill) | Chỉ làm bản đồ; vài mục đáng xem nằm ở repo ngoài, chưa clone |

Kết luận lớn: không nguồn nào cung cấp sẵn **bảng công cụ tĩnh theo ecosystem** (Knip, Vulture, deadcode…), **checklist test flaky/obsolete**, hay **vòng đời Understand→…→Verify**. Ba phần này do bảng bạn paste và kiến thức tác giả skill bổ sung, và phải đối chiếu tài liệu chính thức của từng tool khi viết.

---

## 2. Cách đã làm và giới hạn

- Clone `--depth 1` bằng `git clone` trực tiếp cho 4 repo mới, **không** chạy `scripts/clone_references.sh` (để tránh `git pull` 5 repo cũ). Dòng clone đã được thêm vào script, `bash -n` pass.
- Chỉ đọc file. Không chạy script, hook, `npm install`, hay test của repo nào (R3).
- Kiểm R1: tìm base64, `curl|sh`, "ignore previous", HTML comment, ký tự zero-width trong các file đã đọc → **không thấy gì đáng ngờ**. Hai kết quả cần ghi lại: `awesome-agent-skills/README.md:2040` có badge SVG base64 (ảnh shields, vô hại); `pro-workflow/settings.example.json` chứa luật *chặn* `curl | bash`.
- **Giới hạn độ phủ**: `awesome-copilot` có 463 skill, tôi mở khoảng 8; `pro-workflow` mở khoảng 10 file; `revise-skill` đọc SKILL.md, organization-guidelines và 4/57 pattern. Mục khác chưa đọc.

| Nguồn | Commit | Ngày | License |
|---|---|---|---|
| revise-skill | `4bd8aef` | 2026-05-29 | MIT (David Foster) |
| pro-workflow | `86d5f27` | 2026-09-29 | MIT (`package.json`) |
| awesome-copilot | `dc0083d` | 2026-11-16 | MIT (GitHub) |
| awesome-agent-skills | `20c5716` | 2026-11-15 | MIT (VoltAgent) |

Skill mới viết lại bằng lời riêng, không chép nguyên văn; nguồn được ghi công trong `README.md`.

---

## 3. Nguồn 1: `davidfstr/revise-skill`

**Files đã đọc**: `SKILL.md` (477 dòng), `organization-guidelines.md`, `README.md`, `reference/rename_symbol.md`, `patterns/{dead_code,duplicate_code,obvious_docstrings,hand_rolled_caching}.md`; liệt kê đủ 57 tên pattern.

**Cơ chế**: một skill do người dùng gọi (`disable-model-invocation: true`), nhận `uncommitted` (mặc định) hoặc `last-commit` hoặc danh sách file (`SKILL.md:21-31`). Quy trình 2 lượt (`SKILL.md:33-52`): lượt 1 sửa ngay những thứ nhỏ và cục bộ; thứ gây diff lớn hoặc là tính năng mới thì **hoãn** sang lượt 2; có hai điểm review. Mỗi pattern là một file với *Quick trigger / Why / When NOT / Fix / Before-After*; index chỉ có trigger và snippet ngắn (progressive disclosure).

**Ý mạnh**
- **"When NOT to revise" bắt buộc cho mọi pattern.** `dead_code.md`: không xóa placeholder có TODO, không xóa khi không chắc (gọi động qua `getattr`, template, cross-language), "grep toàn project trước", xóa hẳn chứ không comment-out hay để marker `# removed`.
- `duplicate_code.md`: ngưỡng cụ thể (>3 dòng hoặc cách xa nhau); không gộp khi trùng ngẫu nhiên hoặc phải truyền nhiều tham số; khi buộc trùng thì đánh dấu **mọi bản sao** bằng `NOTE: Duplicated in X and Y` giống hệt nhau để grep ra.
- `obvious_docstrings.md`: docstring nhắc lại tên hàm (đặc biệt trong test AI viết) và banner đầu file.
- Loose pattern "speculative generality": abstraction chỉ có một chỗ dùng, không test → inline (trong `SKILL.md`, mục *Loose patterns*).
- `organization-guidelines.md`: 7-10 mục mỗi cấp, vòng đời pattern; áp dụng được cho chính bộ skill của repo này.
- Học pattern từ commit sửa tay của người dùng (README "How patterns are added").

**Ý yếu hoặc rủi ro**
- Khoảng 45/57 pattern là style Python/JS/TS cá nhân (`local_imports`, `prefer_fstrings`, `if True:` làm khối ẩn danh, `# reinterpret`/`# clone` marker, em-dash, chính tả Anh). Đưa vào skill đa ngôn ngữ sẽ gây nhiễu và mâu thuẫn quy ước của project khác.
- `rename_symbol` phụ thuộc MCP server ngoài (`mcp__revise__*`, tiện ích VS Code); README gọi là tùy chọn.
- Sửa style gây diff lớn: tác giả tự thừa nhận bằng cơ chế "hoãn".

**Adopt / adapt / reject**
- **Adopt**: cấu trúc "When NOT"; xác minh trước khi xóa; xóa hẳn không comment-out; dedup có ngưỡng và ngoại lệ.
- **Adapt**: hai lượt (sửa ngay / hoãn) → báo cáo "Noticed, not changed"; phạm vi mặc định `uncommitted`, rồi `last-commit` → định nghĩa *change set*; marker `NOTE: Duplicated in` → dùng trong `code-simplifier` khi buộc phải trùng.
- **Reject**: 45 pattern style theo ngôn ngữ; MCP `rename_symbol`; chế độ học từ commit (ngoài phạm vi).

---

## 4. Nguồn 2: `rohitg00/pro-workflow`

**Files đã đọc**: `skills/deslop/SKILL.md`, `commands/deslop.md`, `skills/improve-architecture/SKILL.md`, `agents/reviewer.md`, `rules/{module-shape,no-debug-statements,quality-gates}.mdc`, `skills/writing-guidelines/SKILL.md`, đầu `hooks/hooks.json`, danh sách `skills/`, `agents/`, `scripts/`. Không đọc: wiki, orchestrate, learn, cost và các skill còn lại.

**Cơ chế**: plugin Claude Code. `deslop` là skill diff-so-với-`origin/main` rồi tìm slop; phần còn lại (hook Node chạy trên Edit/Write/Bash/commit/push, MCP, wiki, cost tracker) là hạ tầng runtime.

**Ý mạnh**
- `deslop/SKILL.md` (mục *Focus Areas*): comment nói điều hiển nhiên; try/catch phòng thủ trên đường nội bộ tin cậy; cast `any` chỉ để qua type; abstraction cho thao tác một lần; lồng sâu thay vì early return; hack tương thích ngược (`_vars`, re-export, `// removed`); tính năng ngoài yêu cầu; docstring/type annotation thêm vào code **không sửa**; xử lý lỗi cho tình huống không thể xảy ra.
- *Guardrails*: giữ nguyên hành vi, "ba dòng giống nhau tốt hơn một abstraction sớm", xác minh trước khi xóa, tóm tắt 1-3 câu; chạy lại diff để chắc chỉ slop bị xóa.
- **Skill-file mode**: lint chính file SKILL.md (dòng cũ, phình, câu chết, trùng lặp, dừng sớm, thiếu mỏ neo). Ý hay, áp dụng được cho skill của repo này.
- `agents/reviewer.md`: "Không báo finding nào chưa đọc code", phải trích file:line, cấm "consider/ensure/might", grep trước khi nói "thiếu", **"nếu diff sạch thì nói sạch, đừng bịa finding"**.
- `module-shape.mdc`: bề mặt hẹp, thân dày; module chỉ chuyển tiếp là "nông" → inline; **không mock module của chính mình**, chỉ mock ở biên hệ thống; mock theo endpoint thay vì mock `request()` chung.
- `improve-architecture`: map trước, tìm "strain" (module thần, biên rò rỉ, trùng lặp trôi, ranh giới sai, vòng phụ thuộc), đề xuất bước nhỏ nhất, xếp theo đòn bẩy, chỉ chẩn đoán, không viết lại; ADR cho quyết định lớn.
- `no-debug-statements` / `quality-gates`: quét staged tìm debug print, TODO không ticket, secret cứng, code test sót lại.

**Ý yếu hoặc rủi ro**
- `deslop` giả định `origin/main` và `npm test` (JS); Gemini/Codex hoặc repo offline sẽ hỏng. Với thay đổi chưa commit, `origin/main...HEAD` không thấy gì.
- Quy tắc "em-dash là dấu hiệu AI" áp cho văn xuôi, không phải code.
- Hook và MCP là code chạy tự động, mâu thuẫn R3 nếu nhập vào repo này; `settings.example.json` và nhiều biến môi trường API key cho tính năng không liên quan.

**Adopt / adapt / reject**
- **Adopt**: danh sách slop (bỏ phần riêng JS); guardrails; quy tắc bằng chứng của reviewer; module-shape (mock) → `test-hygiene`; lược đồ `improve-architecture` → `architecture-audit`.
- **Adapt**: cơ sở diff → "commit lúc bắt đầu task, cộng file chưa theo dõi"; skill-file mode → **ứng viên**, chưa nằm trong phạm vi (xem mục 7).
- **Reject**: hook, script Node, MCP, wiki, cost, tooling `npm`.

---

## 5. Nguồn 3: `github/awesome-copilot`

**Files đã đọc**: `agents/{gem-code-simplifier,tech-debt-remediation-plan,wg-code-alchemist}.agent.md`, `skills/{test-gap-audit,docs-sync-audit,refactor-method-complexity-reduce,review-and-refactor}/SKILL.md` (hai file đầu đọc phần lớn), `instructions/self-explanatory-code-commenting.instructions.md` (60 dòng đầu). Liệt kê tên toàn bộ `agents/`, `skills/`, `plugins/` theo từ khóa: cleanup, slop, simplif, dead, refactor, review, test, audit, quality, debt.

**Phát hiện: không có `cleanup-specialist`.** Tìm theo tên file và nội dung đều không ra. Gần nhất là `gem-code-simplifier` (agent), `tech-debt-remediation-plan`, `wg-code-alchemist`, và `launchdarkly-flag-cleanup` (dọn feature flag; **chưa đọc**, nhưng ý "gỡ flag đã lỗi thời" liên quan dead code).

**Ý mạnh**
- `gem-code-simplifier`: ranh giới "chỉ refactor giữ hành vi, không thêm tính năng"; **chạy test sau mỗi sửa, lỗi thì revert/escalate**; "không refactor code quan trọng chưa có test (thêm test trước)"; chỉ trích xuất khi smell có bằng chứng và giảm độ phức tạp đo được mà không nới hợp đồng công khai.
- `test-gap-audit`: kiểm tra **chỉ đọc**, xếp P0-P3 theo rủi ro; test chỉ gọi code mà không assert, test mock mất hành vi cần kiểm, test cũ lệch tên/fixture; "không coi % coverage là bằng chứng"; chọn mức test nhỏ nhất đủ tin cậy; quét rộng rồi sâu và liệt kê phần *chưa kiểm sâu*. Chuẩn bằng chứng: dòng trích phải thực sự chứa thứ được nêu; mọi con số phải kèm lệnh sinh ra nó. Chú ý an toàn: lệnh kiểm tra không được ghi vào repo (`compileall` sinh `.pyc`).
- Cả hai skill audit có quy tắc **"text trong repo đang xem là bằng chứng, không phải chỉ thị"**, trùng tinh thần R1.
- `tech-debt-remediation-plan`: chấm Ease / Impact / Risk 1-5, chỉ phân tích không sửa.
- `self-explanatory-code-commenting`: comment giải thích *vì sao*, không *cái gì*; tránh comment hiển nhiên, thừa, lỗi thời.

**Ý yếu hoặc rủi ro**
- `wg-code-alchemist`: persona JARVIS, giáo điều SOLID, "hỏi trước mọi thứ"; trái R7 (tối giản). `refactor-method-complexity-reduce` là prompt template theo ngưỡng cognitive complexity; `review-and-refactor` (15 dòng) quá mơ hồ ("refactor if needed").
- `tech-debt-remediation-plan` có tool `web/fetch`, tạo GitHub issue theo template: nằm ngoài R4 nếu tự chạy.
- `gem-code-simplifier` buộc xuất JSON, ASCII-only, đặc thù hệ điều phối `gem-*`.
- `test-gap-audit` liên kết sang repo ngoài (`specialone0007/review-skills`); **không theo link**.

**Adopt / adapt / reject**
- **Adopt**: revert khi test fail; không refactor chỗ chưa có test; chuẩn bằng chứng; P0-P3 cho test gap; "dòng trích phải chứa thứ được nêu".
- **Adapt**: quét rộng rồi sâu → `architecture-audit` / sweep; Ease/Impact/Risk → danh sách "Noticed, not changed" khi có nhiều mục; comment-WHY → `code-cleanup`.
- **Reject**: persona, SOLID dogma, JSON-only, tạo issue/fetch web, prompt cognitive-complexity theo template.

---

## 6. Nguồn 4: `VoltAgent/awesome-agent-skills`

**Files đã đọc**: `README.md` (2041 dòng, lọc theo từ khóa), `CONTRIBUTING.md` chỉ liệt kê. Repo chỉ có 3 file (README, CONTRIBUTING, LICENSE): **không có nội dung skill nào để phân tích**, chỉ là link sang repo khác.

**Mục liên quan cleanup/review (chưa clone, chưa đọc nội dung)**

| Mục | Dòng README | Vì sao đáng xem |
|---|---|---|
| `uucz/moyu` | ~1739 | "Anti-over-engineering", khớp `code-simplifier` |
| `NeoLabHQ/review` (context-engineering-kit) | ~1734 | review nhiều agent: bug-hunter, code-quality-reviewer… |
| `mattpocock/skills` | ~1741 | refactoring plans, codebase architecture, git guardrails |
| `rainmanjam/poka-yoke` | ~1773 | "làm cho dùng sai không thể biểu diễn" |
| `obra/requesting-code-review`, `receiving-code-review` | ~1715-1716 | repo đã có `receiving-code-review` từ `obra/superpowers` |
| `coderabbitai/skills` | ~1698 | review PR (phụ thuộc dịch vụ ngoài) |
| `MohamedAbdallah-14/unslop`, `manavmishra/zero-slop` | ~1538, ~1652 | slop trong **văn xuôi**, không phải code |

**Adopt / adapt / reject**: nguồn này chỉ cho **danh sách điều tra tiếp**. Không có ý nào được nhập. Tôi không clone các repo ngoài vì spec yêu cầu hỏi trước.

---

## 7. Tổng hợp

### 7.1 Ý tưởng → skill đích

| Skill đích | Lấy gì | Từ nguồn | Xung đột với rule hiện có |
|---|---|---|---|
| `code-cleanup` | Danh sách slop trong change set: comment hiển nhiên/lỗi thời, comment-WHY, try/catch phòng thủ vô lý, cast để qua type, hack tương thích ngược, docstring/annotation thêm vào code không sửa, debug print, TODO không ticket, code test sót, tính năng ngoài yêu cầu; xóa hẳn thay vì comment-out | pro-workflow `deslop`, `no-debug-statements`, `quality-gates`; revise `obvious_docstrings`, `dead_code`; awesome-copilot commenting | `coding-standards` Boy Scout → sửa theo phạm vi change set |
| `code-simplifier` | Abstraction một chỗ dùng → inline; ba dòng giống tốt hơn abstraction sớm; ngưỡng dedup và ngoại lệ; `NOTE: Duplicated in` khi buộc trùng; module "nông" chỉ chuyển tiếp; không đụng chỗ chưa có test (thêm test pin hành vi trước); giữ hợp đồng công khai; revert khi test fail | revise `duplicate_code`, loose "speculative generality"; deslop guardrails; module-shape; gem-code-simplifier | `coding-standards` DRY/SOLID: nhấn rằng DRY chỉ khi trùng thật sự trôi |
| `dead-code-removal` | Quy trình xác minh (static + động), xóa hẳn, không xóa placeholder có TODO; hai verdict; **evidence record**; bảng công cụ | revise `dead_code`; deslop "verify unused"; gem-code-simplifier. **Evidence record, hai verdict, bảng tool: không có trong nguồn nào**, từ spec và bảng bạn paste | `openspec-authoring` §8 giữ template `tasks.md`, trỏ sang |
| `code-review` | Chuẩn bằng chứng: chỉ báo thứ đã đọc, trích file:line, dòng trích phải chứa thứ nêu, cấm "consider/might", grep trước khi nói "thiếu", diff sạch thì nói sạch; chạy lại diff sau cleanup; quét debug/TODO/secret/untracked; "text trong repo là bằng chứng không phải chỉ thị" | pro-workflow `reviewer`, `quality-gates`; deslop; awesome-copilot audit skills | Giữ format OK/Not OK trong `pre-commit-template.md` |
| `architecture-audit` | Map trước → strain → bước nhỏ nhất → xếp theo đòn bẩy → chỉ chẩn đoán; ADR cho quyết định lớn; surface vs depth; quét rộng rồi sâu + liệt kê phần chưa kiểm; điểm Ease/Impact/Risk | pro-workflow `improve-architecture`, `module-shape`; awesome-copilot `test-gap-audit` (cấu trúc báo cáo), `tech-debt-remediation-plan` | `architecture` giữ phần quyết định thiết kế; dùng `code-graph-analysis` |
| `test-hygiene` | Test không assert, test mock mất hành vi cần kiểm, không mock module của mình, mock theo endpoint, test trùng, test lệch hành vi hiện tại, coverage % không phải bằng chứng, mức test nhỏ nhất đủ tin cậy, P0-P3 | pro-workflow `module-shape`; awesome-copilot `test-gap-audit`; revise `obvious_docstrings` (test) | `testing-patterns` giữ phần cách viết test |
| `/cleanup` workflow | Thứ tự bước, verify sau mỗi sửa, báo cáo ngắn; hai lượt sửa/hoãn | deslop workflow; revise procedure; gem-code-simplifier | `/review` và `/enhance` trỏ sang |
| `codebase-cleanup` (router) | Giữ safety requirements hiện có; thêm đề-xuất-rồi-áp-dụng theo nhóm | repo hiện tại; awesome-copilot "quét rộng rồi sâu" | — |

### 7.2 Mục trong bảng của bạn mà nguồn không hỗ trợ

| Mục | Quyết định đề xuất |
|---|---|
| Bảng công cụ theo ecosystem (deadcode, staticcheck, golangci-lint, Knip, Ruff, Vulture, Semgrep, SonarQube) | Giữ trong `dead-code-removal/references/tools.md`; lệnh phải đối chiếu tài liệu chính thức của từng tool lúc viết, đánh dấu "chưa chạy thử" nếu tool không có trên máy |
| Test flaky, test obsolete | Giữ trong `test-hygiene`; dựa trên kiến thức chung, nguồn chỉ hỗ trợ "test lệch hành vi" |
| `cleanup-specialist` agent | Không tồn tại trong nguồn. Đề xuất **không** tạo agent mới; đã gắn skill vào `test-engineer` và `explorer-agent` |
| Hook tự động (CI/pre-commit chặn code thừa) | Ngoài phạm vi; pro-workflow có hook nhưng là code chạy tự động (R3) |

### 7.3 Từ chối có chủ đích
Style Python/JS cá nhân của revise (45 pattern); plugin runtime của pro-workflow; persona và SOLID dogma của Alchemist; tạo issue GitHub / `web/fetch` của tech-debt agent; theo link ra repo ngoài.

### 7.4 Ảnh hưởng đến spec (đã áp dụng hoặc đề xuất)
- Đã áp dụng: tên skill `code-review` (bạn chọn), bỏ golden eval, bạn tự chạy `make install`.
- **Cơ sở change set**: nên ghi rõ "so với commit bắt đầu task; nếu không biết thì `git diff HEAD` + file chưa theo dõi", không giả định `origin/main` (điểm yếu của deslop).
- **Không có agent `cleanup-specialist`**: spec đã để mục "new agent" ở Out of Scope; xác nhận giữ nguyên.
- **Skill-file mode (lint SKILL.md)** của deslop: ứng viên hay, nhưng spec ghi Non-goals "không chạy skill trên code của repo này". **Cần bạn quyết định** (mục 8).

---

## 8. Cần bạn duyệt trước Phase 1

1. Synthesis ở 7.1 có đúng ý không (đặc biệt: `code-review` lấy chuẩn bằng chứng của reviewer, `test-hygiene` có P0-P3)?
2. **Skill-file mode**: thêm vào `code-cleanup` (hoặc `/cleanup skills`) để lint SKILL.md, hay bỏ?
3. Có clone thêm `uucz/moyu`, `mattpocock/skills`, `NeoLabHQ/context-engineering-kit` (review plugin) và `rainmanjam/poka-yoke` để đọc kỹ hơn không? Mặc định: **không**.
4. Phần chưa đọc của `awesome-copilot` (463 skill) và `pro-workflow` (40 skill): chấp nhận mức phủ hiện tại, hay muốn quét thêm theo từ khóa?
