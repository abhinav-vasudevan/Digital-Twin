# Data Inspector for Folders `1/` and `2/`

This tool inventories your two data folders, parses attributes from filenames/paths (sex, region, diet type, activity, weight class, category), samples text from PDFs/DOCX, and produces both JSON and Markdown reports.

## Setup (Windows PowerShell)

```powershell
cd "d:\Documents\Diet plan"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r data-inspector\requirements.txt
```

## Run

```powershell
python data-inspector\discover.py --folders "D:\Documents\Diet plan\1" "D:\Documents\Diet plan\2" --out "D:\Documents\Diet plan\data-inspector\report"
```

Outputs:
- `data-inspector/report/inventory.json` — per-file metadata and aggregates
- `data-inspector/report/understanding.md` — human-readable summary

## What it extracts
- File inventory and sizes
- Attributes parsed from filenames and parent folders:
  - `sex` (male/female)
  - `region` (north_indian/south_indian)
  - `diet_type` (veg/eggetarian/non_veg)
  - `activity` (sedentary/light/moderate/heavy)
  - `weight_class` (underweight/normal/overweight/obese)
  - `category` (pcos, type_1_diabetes, skin, gut, liver_detox, probiotic, weight_loss, weight_gain, anti_inflammatory, anti_aging_skin, high_protein, high_protein_high_fiber, detox)
- Text sample and textability:
  - For PDFs: first-page text sample; heuristic whether it has selectable text
  - For DOCX: paragraph text sample

## Next steps
- If many PDFs are scanned (no text), enable OCR (tesseract + pytesseract) in a future step.
- Extend parsers for additional attributes present in naming conventions.
