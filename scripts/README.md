# Scripts Directory

Utility scripts for the Diet Plan application.

## Available Scripts

### `serve.ps1` (Windows PowerShell)
Start the FastAPI development server.

**Usage from project root:**
```powershell
.\scripts\serve.ps1
```

**Options:**
- `-Host <address>` - Server host (default: 127.0.0.1)
- `-Port <number>` - Server port (default: 8000)
- `-Open` - Automatically open browser
- `-Background` - Run server in background

**Examples:**
```powershell
# Start server normally
.\scripts\serve.ps1

# Start and open browser
.\scripts\serve.ps1 -Open

# Custom port
.\scripts\serve.ps1 -Port 5000

# Background mode
.\scripts\serve.ps1 -Background
```

### `init_data.sh` (Linux/Mac)
Initialize empty data files for the application.

**Usage from project root:**
```bash
bash scripts/init_data.sh
```

### Other Scripts
- `age_matching_analysis.py` - Analyze age matching in diet plans
- `debug_weight_gain.py` - Debug weight gain recommendations
- `download_phi2_model.py` - Download Phi-2 model for local use
- `install_nutritionverse.ps1` - Install nutritionverse dataset
