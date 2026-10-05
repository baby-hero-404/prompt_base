# Makefile Standards

> Convention dùng chung cho `Makefile` ở mọi project (Node, Go, Python, frontend, backend...).
> Đây là tài liệu **quy ước** — không phải một file để include. Mỗi project tự viết `Makefile`
> riêng theo chuẩn này, map các target sau sang tool thật của stack đó.

---

## Nguyên tắc

1. **Tên target cố định** — dùng đúng tên ở bảng dưới, không đổi tên tương đương (không `tests`, `linting`, `setup`...).
2. **`help` là target đầu tiên và là default** (`.DEFAULT_GOAL := help`) — chạy `make` không có argument phải in ra danh sách target, không chạy việc gì khác.
3. **Mỗi target có 1 dòng comment ngay trên nó**, dùng format `## <mô tả ngắn>` để `help` tự parse được (xem mẫu bên dưới).
4. **Target không tồn tại cho stack đó thì bỏ qua, không tạo no-op rỗng.** Ví dụ project không có bước `build` (script thuần) thì không khai báo `build:`.
5. **Không gọi trực tiếp tool trong nhiều dòng phức tạp** — nếu logic dài hơn 1-2 lệnh, đẩy ra `scripts/<name>.sh` và gọi từ Makefile.
6. **Khai báo `.PHONY`** cho mọi target (không file thật nào trùng tên).

---

## Bộ target chuẩn

| Target | Bắt buộc | Ý nghĩa |
|---|---|---|
| `help` | Có | Liệt kê toàn bộ target kèm mô tả. Default goal. |
| `install` | Có | Cài dependency / setup môi trường local (idempotent). |
| `clean` | Có | Xóa build artifact, cache, venv phát sinh — không đụng source/data người dùng. |
| `lint` | Có | Static check (formatter + linter), không sửa file (chế độ check-only). |
| `test` | Có | Chạy test suite (unit + integration nếu có), exit non-zero khi fail. |
| `upgrade` | Có | Nâng toàn bộ dependency lên bản mới nhất (giống `go get -u ./... && go mod tidy`), sau đó tự chạy `test` để phát hiện breaking change ngay. |
| `build` | Nếu áp dụng | Compile/bundle ra artifact deploy được. |
| `deploy` | Nếu áp dụng | Theo 5-phase deployment process trong `CLAUDE.md`; không chạy ngầm ngoài giờ xác nhận với user. |
| `release` | Nếu áp dụng | Tag version + publish artifact/package. Tách khỏi `deploy` (release = đóng gói, deploy = đưa lên môi trường). |

### Target phụ thường gặp (không bắt buộc, tên phải theo mẫu này nếu có)

- `fmt` — auto-format (khác `lint`, lint chỉ check không sửa).
- `dev` — chạy ở local dev mode (hot reload/watch).
- `audit` — security/dependency audit (map tới `security-auditor` agent khi cần).

---

## Mẫu `help` tự document

```make
.DEFAULT_GOAL := help

.PHONY: help
help: ## Hiện danh sách target
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Cài dependency, setup môi trường local
	@echo "TODO: install steps"

.PHONY: clean
clean: ## Xóa build artifact và cache
	@echo "TODO: clean steps"

.PHONY: lint
lint: ## Chạy static check, không sửa file
	@echo "TODO: lint steps"

.PHONY: test
test: ## Chạy test suite
	@echo "TODO: test steps"

.PHONY: upgrade
upgrade: ## Nâng dependency lên bản mới nhất rồi chạy test
	@echo "TODO: upgrade deps steps (ví dụ: go get -u ./... && go mod tidy)"
	@$(MAKE) test
```

### Mapping `upgrade` theo stack (ví dụ)

| Stack | Lệnh upgrade |
|---|---|
| Go | `go get -u ./... && go mod tidy` |
| Node (npm) | `npm update && npm outdated` (hoặc `npx npm-check-updates -u && npm install` nếu muốn lên major) |
| Node (pnpm) | `pnpm update --latest` |
| Python (pip) | `pip install --upgrade -r requirements.txt` (hoặc `pip-compile --upgrade` nếu dùng pip-tools) |
| Python (poetry) | `poetry update` |

Mọi target khác (`build`, `deploy`, `release`, `fmt`, `dev`, `audit`...) copy đúng pattern
`<name>: ## <mô tả>` để `help` tự nhận ra.

---

## Checklist khi tạo/chuẩn hóa Makefile cho một project

- [ ] `help` là default goal, chạy `make` không argument in đúng danh sách.
- [ ] Có đủ 5 target bắt buộc: `install`, `clean`, `lint`, `test`, `upgrade`.
- [ ] `build`/`deploy`/`release` có mặt nếu stack cần, đặt tên đúng chuẩn (không đồng nghĩa khác).
- [ ] Mỗi target có `## comment` và nằm trong `.PHONY`.
- [ ] Logic dài được tách ra `scripts/`, Makefile chỉ gọi.
- [ ] `deploy`/`release` không chạy tự động trong CI mà chưa được xác nhận — theo nguyên tắc "ask before destructive/irreversible" trong `CLAUDE.md`.

---

## Ghi chú về repo này (`prompt_base`)

`Makefile` ở root repo này **không** theo chuẩn trên — nó là tooling đặc thù cho framework
prompt-base (registry, skill-check, install-claude/install-gemini, memory-*) và không nên bị
map cứng vào bộ target chuẩn ở trên. Khi tạo Makefile cho các project ứng dụng khác (ngoài
prompt-base), dùng tài liệu này làm chuẩn.
