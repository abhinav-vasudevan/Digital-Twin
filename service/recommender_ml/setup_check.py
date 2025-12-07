"""
Quick Setup Script for ML Recommender

This script:
1. Checks dependencies
2. Generates embeddings if needed
3. Tests the ML recommender
4. Provides setup instructions
"""

import subprocess
import sys
from pathlib import Path

def check_package(package_name):
    """Check if a Python package is installed"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def check_ollama():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def main():
    print("=" * 60)
    print("ML RECOMMENDER SETUP CHECK")
    print("=" * 60)
    
    # Check Python packages
    print("\n1. Checking Python Dependencies...")
    required_packages = {
        'sentence_transformers': 'sentence-transformers',
        'numpy': 'numpy',
        'faiss': 'faiss-cpu',
        'ollama': 'ollama'
    }
    
    missing = []
    for import_name, pip_name in required_packages.items():
        if check_package(import_name):
            print(f"  ✅ {pip_name}")
        else:
            print(f"  ❌ {pip_name} - NOT INSTALLED")
            missing.append(pip_name)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print(f"\nInstall with:")
        print(f"  pip install {' '.join(missing)}")
        print("\nNote: These are optional. System will work with fallback if not installed.")
    else:
        print("\n✅ All Python packages installed!")
    
    # Check Ollama
    print("\n2. Checking Ollama...")
    if check_ollama():
        print("  ✅ Ollama is installed")
        
        # Check for models
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if 'llama' in result.stdout.lower():
            print("  ✅ Llama model found")
        else:
            print("  ⚠️  No Llama model found")
            print("  Install with: ollama pull llama3.2:3b")
    else:
        print("  ❌ Ollama not installed")
        print("  Install from: https://ollama.ai")
        print("  Or use: winget install Ollama.Ollama")
    
    # Check embeddings
    print("\n3. Checking Embeddings...")
    embeddings_path = Path(__file__).parent.parent / "outputs" / "pdf_embeddings.npy"
    if embeddings_path.exists():
        print(f"  ✅ Embeddings found: {embeddings_path}")
    else:
        print(f"  ⚠️  Embeddings not found: {embeddings_path}")
        print("  Will be created on first run (takes ~2 minutes)")
    
    # Check PDF index
    print("\n4. Checking PDF Index...")
    index_path = Path(__file__).parent.parent / "outputs" / "pdf_index.json"
    if index_path.exists():
        print(f"  ✅ PDF index found: {index_path}")
    else:
        print(f"  ❌ PDF index not found: {index_path}")
        print("  Run pdf indexing first!")
    
    # Summary
    print("\n" + "=" * 60)
    print("SETUP STATUS")
    print("=" * 60)
    
    if not missing and check_ollama() and index_path.exists():
        print("✅ READY TO USE!")
        print("\nThe ML recommender is ready for production use.")
        print("\nTest it:")
        print("  python -c \"from service.recommender_ml import MLRecommender; r = MLRecommender(); print('OK')\"")
    elif not index_path.exists():
        print("❌ CRITICAL: PDF Index missing")
        print("\nCreate index first before using ML recommender")
    else:
        print("⚠️  PARTIALLY READY")
        print("\nML recommender will work with reduced functionality:")
        print("  - Without sentence-transformers: Uses keyword search")
        print("  - Without Ollama: Returns meals without LLM generation")
        print("  - Without embeddings: Will create on first run")
        print("\nFor full functionality, install missing components above.")
    
    # Optional: Test
    print("\n" + "=" * 60)
    print("QUICK TEST (Optional)")
    print("=" * 60)
    print("\nWant to test the ML recommender? (y/n): ", end="")
    
    try:
        response = input().strip().lower()
        if response == 'y':
            print("\nTesting ML recommender...")
            try:
                from service.recommender_ml import MLRecommender
                recommender = MLRecommender()
                print("✅ ML recommender initialized successfully!")
                
                # Test recommendation
                test_profile = {
                    "gender": "female",
                    "age": 28,
                    "height": 160,
                    "weight": 65,
                    "bmi_category": "overweight",
                    "activity_level": "moderate",
                    "diet_type": "vegetarian",
                    "region": "north_indian",
                    "goal": "weight_loss"
                }
                
                print("\nGenerating test recommendation...")
                result = recommender.recommend(test_profile, top_k=3)
                
                if result.get('status') == 'success':
                    print("✅ Recommendation generated successfully!")
                    print(f"   Method: {result.get('method')}")
                    print(f"   Sources: {result.get('metadata', {}).get('total_sources', 0)}")
                    print(f"   Meals: {result.get('metadata', {}).get('total_meals_available', 0)}")
                else:
                    print(f"⚠️  Status: {result.get('status')}")
                    print(f"   Message: {result.get('message', 'Unknown')}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                print("\nCheck the error and fix dependencies")
    except KeyboardInterrupt:
        print("\n\nSkipped test.")
    
    print("\n" + "=" * 60)
    print("For more information, see: service/recommender_ml/README.md")
    print("=" * 60)

if __name__ == "__main__":
    main()
