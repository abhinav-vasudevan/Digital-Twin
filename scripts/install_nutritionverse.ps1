# Install NutritionVerse-Real ML Recommender
# Run this script to install all dependencies

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "NUTRITIONVERSE-REAL ML RECOMMENDER INSTALLATION" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "1. Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "  ✗ Python not found!" -ForegroundColor Red
    Write-Host "  Install Python 3.8+ from: https://www.python.org" -ForegroundColor Red
    exit 1
}

# Check CUDA (for GPU)
Write-Host ""
Write-Host "2. Checking CUDA (GPU support)..." -ForegroundColor Yellow
try {
    $nvidiaSmi = nvidia-smi 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ NVIDIA GPU detected" -ForegroundColor Green
        Write-Host "  Installing PyTorch with CUDA support..." -ForegroundColor Cyan
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    }
} catch {
    Write-Host "  ⚠ No NVIDIA GPU detected" -ForegroundColor Yellow
    Write-Host "  Installing CPU-only PyTorch (slower)..." -ForegroundColor Cyan
    pip install torch torchvision torchaudio
}

# Install core dependencies
Write-Host ""
Write-Host "3. Installing NutritionVerse dependencies..." -ForegroundColor Yellow
Write-Host "  This may take several minutes..." -ForegroundColor Cyan
pip install transformers accelerate sentence-transformers numpy faiss-cpu

# Install fine-tuning dependencies (optional)
Write-Host ""
Write-Host "4. Installing fine-tuning dependencies..." -ForegroundColor Yellow
$response = Read-Host "Install fine-tuning tools? (Y/n)"
if ($response -ne "n" -and $response -ne "N") {
    pip install peft datasets bitsandbytes
    Write-Host "  ✓ Fine-tuning tools installed" -ForegroundColor Green
} else {
    Write-Host "  Skipped (you can install later)" -ForegroundColor Yellow
}

# Verify installation
Write-Host ""
Write-Host "5. Verifying installation..." -ForegroundColor Yellow

$verifyScript = @"
import sys
try:
    import transformers
    import torch
    import sentence_transformers
    import numpy
    import faiss
    
    print('✓ All core packages installed')
    print(f'  PyTorch: {torch.__version__}')
    print(f'  CUDA available: {torch.cuda.is_available()}')
    
    if torch.cuda.is_available():
        print(f'  GPU: {torch.cuda.get_device_name(0)}')
        print(f'  VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB')
    
    sys.exit(0)
except ImportError as e:
    print(f'✗ Missing package: {e}')
    sys.exit(1)
"@

$verifyResult = python -c $verifyScript
if ($LASTEXITCODE -eq 0) {
    Write-Host $verifyResult -ForegroundColor Green
} else {
    Write-Host $verifyResult -ForegroundColor Red
}

# Summary
Write-Host ""
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "INSTALLATION COMPLETE" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. NutritionVerse-Real will download automatically on first use (~14GB)" -ForegroundColor White
Write-Host "2. Test the system:" -ForegroundColor White
Write-Host "   cd service" -ForegroundColor Gray
Write-Host "   python api.py" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Optional: Fine-tune on your 460 PDFs" -ForegroundColor White
Write-Host "   See: service/recommender_ml/FINE_TUNING_GUIDE.md" -ForegroundColor Gray
Write-Host ""
Write-Host "Model: AweXiaoXiao/NutritionVerse-Real-7B" -ForegroundColor Cyan
Write-Host "Documentation: service/recommender_ml/README.md" -ForegroundColor Cyan
Write-Host ""
