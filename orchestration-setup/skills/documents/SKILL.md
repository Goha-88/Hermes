---
name: documents
description: |
  Produce finished document deliverables — proposals (КП), presentations,
  spreadsheets, reports, contracts — as .docx / .pptx / .xlsx / .pdf files.
  Use when asked to "make a deck / proposal / КП / Excel / Word doc / report /
  договор".
---

# Document production

Generate real office files via code execution. Available libraries:
`python-docx`, `python-pptx`, `openpyxl`, `pandas`, `matplotlib`, `reportlab`/`pypdf`.

Workflow:
1. Clarify the deliverable, audience, and key content only if not obvious (one short question max).
2. Write a python script that builds the file and saves it (e.g. under `~/.hermes/`).
3. Run it in the terminal; verify the file exists and is non-empty.
4. Send/attach the file to the user.

By format:
- **Word** (КП, договор, отчёт) → `python-docx`: headings, tables, styles.
- **Slides** (презентация) → `python-pptx`: title + content slides; ≤6 bullets per slide.
- **Excel** (финмодель, прайс, таблица) → `openpyxl`: sheets, formulas, number formats.
- **PDF** → build docx/pptx then convert, or `reportlab`.

For customer-facing text and visual style follow the `brand-voice` skill.
For charts inside documents use the `data-analysis` skill.
Surface the cost if a paid model was used to draft the content.
