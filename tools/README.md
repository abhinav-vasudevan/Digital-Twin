# PDF Extractor (Text + Tables)

A tiny helper to extract text (and optionally tables) from PDFs in your workspace.

## Setup (Windows PowerShell)

```powershell
# From the workspace root
cd "d:\Documents\Diet plan"

# Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r tools\requirements.txt
```

## Usage

Extract text from all PDFs under the workspace:

```powershell
python tools\pdf_extract.py --root "d:\Documents\Diet plan" --pattern "**/*.pdf"
```

Also extract tables into per-PDF Excel files (`*_tables.xlsx`):

```powershell
python tools\pdf_extract.py --root "d:\Documents\Diet plan" --pattern "**/*.pdf" --tables
```

Write outputs into a separate folder while preserving structure:

```powershell
python tools\pdf_extract.py --root "d:\Documents\Diet plan" --pattern "**/*.pdf" --tables --out-dir outputs
```

Process only the first N pages (useful for testing):

```powershell
python tools\pdf_extract.py --root "d:\Documents\Diet plan" --pattern "**/*.pdf" --max-pages 2
```

Overwrite existing outputs:

```powershell
python tools\pdf_extract.py --root "d:\Documents\Diet plan" --pattern "**/*.pdf" --overwrite
```

## Notes
- If a PDF is a scanned image (no embedded text), text extraction may be empty. OCR can be added later if needed.
- Tables are best-effort; complex layouts may require manual cleanup.
- Outputs default to the same folder as each PDF unless `--out-dir` is provided.
