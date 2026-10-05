---
name: makefile-standards
description: "Use when creating, editing, or reviewing a Makefile for any project, to apply a consistent, synced target convention (help, install, clean, lint, test, upgrade, build, deploy, release) across all projects. Triggers on: makefile, make target, make mod, upgrade dependencies."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Makefile Standards

> Convention dùng chung cho `Makefile` ở mọi project (Node, Go, Python, frontend, backend...).
> Áp dụng khi tạo mới hoặc chỉnh sửa Makefile của bất kỳ project nào — không áp dụng ngược
> cho tooling nội bộ của framework prompt-base (xem Exceptions).

## When to Use
- Tạo Makefile mới cho một project.
- Được yêu cầu "chuẩn hóa"/"đồng bộ" Makefile giữa nhiều project.
- Review một Makefile có sẵn và phát hiện target lệch chuẩn.

## Core Principles
1. **Tên target cố định** — dùng đúng tên: `help`, `install`, `clean`, `lint`, `test`, `upgrade`,
   và khi áp dụng: `build`, `deploy`, `release`. Không dùng tên tương đương (`tests`, `setup`,
   `linting`, `update`).
2. **`upgrade` = nâng toàn bộ dependency lên bản mới nhất** (giống `go get -u ./... && go mod
   tidy` ở Go) rồi **tự chạy `test` ngay sau** để phát hiện breaking change. Khác với `install`
   (chỉ cài đúng theo lock file hiện có, không đổi version).
2. **`help` là default goal** (`.DEFAULT_GOAL := help`) — `make` không argument chỉ in danh sách
   target, không chạy side effect nào khác.
3. **Mỗi target có dòng `## <mô tả ngắn>` ngay trên nó** để `help` tự parse (xem Reference).
4. **Không tạo target rỗng/no-op** cho thứ project không có — bỏ qua target đó hoàn toàn.
5. **Logic dài (>1-2 lệnh) đẩy ra `scripts/<name>.sh`**, Makefile chỉ gọi script.
6. Mọi target khai báo trong `.PHONY`.
7. `deploy`/`release` không chạy tự động/ngầm chưa xác nhận — tuân theo nguyên tắc
   "ask before destructive/irreversible" trong `CLAUDE.md` và 5-phase deployment process.

Xem bảng target đầy đủ, mẫu `help` tự document, và checklist trong
`references/makefile-standards.md`.

## Anti-Patterns
- Đổi tên target chuẩn (`setup` thay cho `install`, `tests` thay cho `test`) → phá đồng bộ
  giữa các project.
- Nhồi logic dài, nhiều dòng `&&`/`;` trực tiếp vào target thay vì tách ra `scripts/`.
- Thêm `deploy`/`release` tự chạy trong CI mà không có bước xác nhận.
- Copy cứng target của framework prompt-base (`registry`, `skill-check`, `memory-*`...) vào
  project ứng dụng khác — đó là tooling riêng, không phải chuẩn chung.

## Exceptions
`Makefile` ở root repo `prompt_base` **không** theo chuẩn này — nó là tooling đặc thù cho
framework (registry, skill-check, install-claude/install-gemini, memory-*). Chuẩn này chỉ áp
dụng khi tạo/sửa Makefile cho các project ứng dụng khác.
