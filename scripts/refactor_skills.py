import os
import re

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text)
    return text.strip('-')

def extract_references():
    skill_root = "./skills"
    if os.path.exists(skill_root):
        for d in os.listdir(skill_root):
            d_path = os.path.join(skill_root, d)
            skill_md = os.path.join(d_path, "SKILL.md")
            if not os.path.exists(skill_md): continue

            with open(skill_md, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if len(lines) <= 150:
                continue

            # Attempt to extract sections from the bottom
            # We look for ## or ### headers, but not inside fenced code blocks
            # (example output templates often contain literal "##"/"###" lines).
            sections = []
            current_section = []
            current_header = ""
            in_code_fence = False

            for line in lines:
                if re.match(r'^\s*```', line):
                    in_code_fence = not in_code_fence
                    current_section.append(line)
                    continue
                if not in_code_fence and re.match(r'^#{2,3}\s+(.+)', line):
                    if current_section:
                        sections.append((current_header, current_section))
                    current_header = line
                    current_section = [line]
                else:
                    current_section.append(line)

            if current_section:
                sections.append((current_header, current_section))

            if len(sections) < 3:
                continue # Not enough sections to split safely

            # Keep top sections (frontmatter, intro, etc)
            kept_lines = []
            if not sections[0][0]: # frontmatter
                kept_lines.extend(sections[0][1])
                sections.pop(0)

            # Pop sections from the bottom until the main file fits the budget.
            # Collect everything popped into ONE consolidated reference file per
            # skill (not one file per header) — a handful of small files each
            # holding a coherent chunk of content, matching how reference docs
            # are written by hand elsewhere in this repo (e.g. typescript-expert,
            # python-patterns), instead of a pile of near-empty fragments.
            extracted = []  # list of (title, content_lines), in original order
            while len(kept_lines) + sum(len(s[1]) for s in sections) > 130 and len(sections) > 2:
                header, content = sections.pop()
                if not header:
                    continue
                title = re.match(r'^#{2,3}\s+(.+)', header).group(1).strip()
                extracted.insert(0, (title, content))

            for header, content in sections:
                kept_lines.extend(content)

            if extracted:
                ref_dir = os.path.join(d_path, "references")
                if not os.path.exists(ref_dir):
                    os.makedirs(ref_dir)

                ref_lines = []
                for title, content in extracted:
                    ref_lines.extend(content)
                ref_file = os.path.join(ref_dir, "extended-reference.md")
                with open(ref_file, "w", encoding="utf-8") as f:
                    f.writelines(ref_lines)

                kept_lines.append("\n## Extended References\n")
                kept_lines.append(
                    "For less-frequently-needed detail, see "
                    "[`references/extended-reference.md`](references/extended-reference.md):\n"
                )
                for title, _ in extracted:
                    kept_lines.append(f"- {title}\n")

                with open(skill_md, "w", encoding="utf-8") as f:
                    f.writelines(kept_lines)
                print(f"Refactored {d_path} (now {len(kept_lines)} lines, {len(extracted)} sections moved to references/extended-reference.md)")

if __name__ == "__main__":
    extract_references()
