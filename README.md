# Son Spectacles Context Budget Estimator

A small local/Streamlit tool for estimating how much model context a **Son Spectacles** task may consume after the prompt and reference files are parsed.

The key metric is **extracted text tokens**, not file size in MB. A small text-dense PDF or workbook can consume far more context than a larger image-heavy file.

## Son Spectacles reference-file rules

The current project guidelines allow **1–16 reference files** using these file types:

- PDF (`.pdf`)
- Word (`.docx`)
- PowerPoint (`.pptx`)
- Excel (`.xlsx`)
- CSV (`.csv`)
- Text (`.txt`)
- JSON (`.json`)
- Python (`.py`)
- Markdown (`.md`)
- HTML (`.html`)
- XML (`.xml`)

The estimator supports the same set.

## Context limit

The app defaults to **100,000 tokens**, matching the existing Spidey estimator, but the limit is editable.

This should be treated as a configurable planning value rather than an official Son Spectacles limit: the project guidelines define allowed files and file counts, but do not state a model context ceiling. If Ops provides a different limit for a runner/model, enter that value in the app.

## Install

```bash
git clone https://github.com/Norsetune/son-spectacles-token-estimator.git
cd son-spectacles-token-estimator
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the Streamlit app

```bash
streamlit run streamlit_app.py
```

Then open the local URL shown in Terminal.

1. Paste the Son Spectacles task prompt.
2. Upload the task's reference files.
3. Set the context limit if the current runner/model uses something other than the default.
4. Click **Estimate context budget**.

The app reports:

- total estimated extracted tokens
- percentage of the selected context limit
- risk band
- per-file token estimates
- largest contributors
- reference-file count against the Son Spectacles 16-file cap
- downloadable CSV report

## Run from the command line

Estimate a folder of reference files:

```bash
python token_estimator.py /path/to/reference_files
```

Include a prompt stored in a text file:

```bash
python token_estimator.py /path/to/reference_files --prompt-file prompt.txt
```

Use a different context limit:

```bash
python token_estimator.py /path/to/reference_files --prompt-file prompt.txt --limit 200000
```

Write a JSON report:

```bash
python token_estimator.py /path/to/reference_files --prompt-file prompt.txt --json-out report.json
```

## Risk bands

Risk bands are percentages of the selected context limit:

- **SAFE:** under 70%
- **CLOSE_TO_LIMIT:** 70–85%
- **LIKELY_OVER_LIMIT_SOON:** 85–95%
- **CRITICAL:** 95–100%
- **OVER_LIMIT:** 100%+

Individual files also receive a `WATCH` band from 40–70% to make unusually large single contributors easier to spot.

## Notes and caveats

- This is an estimate, not the exact tokenizer used by every Son Spectacles model/runner.
- When available, the tool uses `tiktoken` with `cl100k_base` as a proxy tokenizer.
- If `tiktoken` is unavailable, it falls back to a conservative character/word heuristic.
- PDF extraction uses embedded text only; image-only/scanned PDFs are **not OCR-scanned** and can therefore be underestimated.
- Hidden system prompts, file wrappers, table serialization, images, tool metadata, and the model's response also consume context.
- Excel estimates are based on non-empty cell contents/formulas, not workbook file size or visual formatting.
- The estimator is intended for the **prompt + reference files** supplied to the model. Gold deliverables are not part of that input budget.

## Relationship to Spidey

This project is intentionally based on the existing [Spidey Context Budget Estimator](https://github.com/Norsetune/spidey-token-estimator), with Son Spectacles branding and project-specific file/count handling.

---

Kenneth Pedersen · 2026
