# Pipeline Tools

Bulk extraction and normalization utilities for folders `1/` and `2/`.

## Setup (Windows PowerShell)

```powershell
cd "D:\Documents\Diet plan"
# Reuse existing venv
.\.venv\Scripts\Activate.ps1

# Install any extra packages if needed
pip install pdfplumber python-docx pandas openpyxl
```

## Extract text from all plans

```powershell
python pipeline\extract_text.py --roots "D:\Documents\Diet plan\1" "D:\Documents\Diet plan\2" --out "D:\Documents\Diet plan\outputs\raw" --tables
```

Outputs mirror the source structure under `outputs/raw/1/` and `outputs/raw/2/`, with `.txt` for text and optional `*_tables.xlsx` for tables.

## Next
- Add `structure_parser.py` to split meals/sections and normalize units.
- Add `ocr_fallback.py` for scanned PDFs (if discovered in future).
