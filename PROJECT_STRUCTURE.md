# 📁 Project Structure

This document explains the organized folder structure of the Diet Plan application.

## Directory Layout

```
Diet plan/
├── 📂 service/                  # Main application code
│   ├── api.py                  # FastAPI application & routes
│   ├── pdf_parser.py           # PDF parsing logic
│   ├── pdf_recommender.py      # PDF-based recommendation system
│   ├── llama_service.py        # Llama model integration
│   ├── recommender_exact/      # Exact match recommender
│   ├── recommender_goal/       # Goal-based recommender
│   ├── recommender_ml/         # ML-based recommender (RAG)
│   ├── templates/              # HTML templates
│   ├── static/                 # CSS, JS, images
│   └── data/                   # User data JSON files
│
├── 📂 tests/                    # All test files
│   ├── test_*.py               # Unit and integration tests
│   ├── check_*.py              # Verification scripts
│   └── analyze_coverage.py     # Coverage analysis
│
├── 📂 scripts/                  # Utility scripts
│   ├── serve.ps1               # Start development server (Windows)
│   ├── init_data.sh            # Initialize data files (Linux/Mac)
│   ├── age_matching_analysis.py
│   ├── debug_weight_gain.py
│   └── download_phi2_model.py
│
├── 📂 docs/                     # Documentation
│   ├── QUICK_START.md
│   ├── HOW_TO_USE_WEBSITE.md
│   ├── LLAMA_FOOD_MODEL_SETUP.md
│   ├── TESTING_GUIDE.md
│   └── ... (14 markdown files)
│
├── 📂 notebooks/                # Jupyter notebooks
│   ├── Colab_Llama_FoodModel.ipynb  # Llama-3 food model on Colab
│   └── Colab_Phi2_Server.ipynb      # Phi-2 model server on Colab
│
├── 📂 training/                 # Model training code
│   ├── colab_model_server.py   # Colab model server
│   └── Diet model phi - 2/     # Phi-2 training data
│
├── 📂 data/                     # Sample data and datasets
│   ├── overall total diet plans (1) (1).xlsx
│   ├── diya/                   # Dataset folder
│   └── kg/                     # Knowledge graph data
│
├── 📂 outputs/                  # Generated files
│   ├── pdf_index.json          # Main PDF index (CRITICAL)
│   └── raw/                    # Extracted PDF text
│
├── 📂 pipeline/                 # Data processing pipeline
│   ├── build_pdf_index.py      # Build searchable index
│   ├── extract_text.py         # PDF text extraction
│   └── structure_parser.py     # Parse meal structures
│
├── 📂 tools/                    # Developer tools
│   ├── data-inspector/         # Inspect and analyze data
│   └── ...
│
├── 📂 Diet plans/               # Source PDF files (460 plans)
│
├── wsgi.py                     # WSGI entry point for deployment
├── requirements.txt            # Python dependencies
├── render.yaml                 # Render.com deployment config
└── readme.md                   # Project overview
```

## Key Files

### Application Entry Points
- **`service/api.py`** - Main FastAPI application with all routes
- **`wsgi.py`** - WSGI wrapper for deployment on PythonAnywhere/Gunicorn
- **`scripts/serve.ps1`** - Development server startup script (Windows)

### Critical Data Files
- **`outputs/pdf_index.json`** - Searchable index of all 460 diet plans (MUST exist)
- **`service/data/*.json`** - User profiles, meal plans, daily logs

### Model Notebooks
- **`notebooks/Colab_Llama_FoodModel.ipynb`** - Run Llama-3 8B food model on Colab GPU
- **`notebooks/Colab_Phi2_Server.ipynb`** - Run Phi-2 model on Colab (deprecated)

### Documentation
- **`docs/HOW_TO_USE_WEBSITE.md`** - User guide for the web interface
- **`docs/LLAMA_FOOD_MODEL_SETUP.md`** - Setup guide for Colab ML model
- **`docs/QUICK_START.md`** - Quick start guide for developers

## Running the Application

### Start Development Server (Windows)
```powershell
.\scripts\serve.ps1
```

### Start Development Server (Manual)
```bash
# From project root
python -m uvicorn service.api:app --reload --port 8000
```

### Access the Application
- **Web UI:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Recommendations:** http://localhost:8000/get-recommendations

## Important Notes

1. **All paths are relative** - Scripts work from project root
2. **PDF index required** - Run `python pipeline/build_pdf_index.py` if missing
3. **Virtual environment** - Create `.venv` in project root before running
4. **Colab integration** - Update ngrok URL in `service/recommender_ml/ml_recommender.py` (line 20)

## Migration Notes

Files have been organized from flat structure to categorized folders:
- Test files moved to `tests/`
- Documentation moved to `docs/`
- Utility scripts moved to `scripts/`
- Notebooks moved to `notebooks/`
- Training code moved to `training/`

All imports and paths have been updated to work with the new structure.
