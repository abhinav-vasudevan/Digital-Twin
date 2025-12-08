"""
Download COMPLETE Llama-3 Food/Nutrition Model - Fully Offline
Downloads BASE model + Food/Nutrition LoRA adapter
Total size: ~16GB - Everything offline, no internet needed in Colab
"""
from huggingface_hub import snapshot_download, login
import os
from pathlib import Path

print("=" * 70)
print("🔐 HUGGINGFACE AUTHENTICATION")
print("=" * 70)
print("\n📝 Enter your HuggingFace token")
print("   Get token: https://huggingface.co/settings/tokens")
print("   Important: Accept Llama-3 license first:")
print("   Visit: https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct\n")

hf_token = input("Enter your HuggingFace token: ").strip()

if not hf_token:
    print("❌ Token required. Exiting.")
    exit()

try:
    login(token=hf_token)
    print("✅ Authenticated successfully!\n")
except Exception as e:
    print(f"❌ Authentication failed: {e}")
    exit()

print("=" * 70)
print("🚀 DOWNLOADING COMPLETE OFFLINE MODEL")
print("=" * 70)
print("\n📦 This will download:")
print("   1. Base Llama-3-8B-Instruct (~15.9GB)")
print("   2. Food/Nutrition LoRA Adapter (~100MB)")
print("   Total: ~16GB")
print("\n⚠️  This is a COMPLETE download - fully offline")
print("⚠️  No internet needed in Colab after upload")
print("⚠️  Download time: 1-2 hours (depending on internet speed)")
print("⚠️  Make sure you have 20GB free disk space\n")

confirm = input("Continue? (yes/no): ")
if confirm.lower() != 'yes':
    print("❌ Download cancelled.")
    exit()

try:
    # Download 1: Base Llama-3-8B Model
    print("\n" + "=" * 70)
    print("📥 STEP 1/2: Downloading Base Llama-3-8B (~15.9GB)")
    print("=" * 70)
    print("⏳ This will take 1-2 hours...\n")
    
    base_model = "meta-llama/Meta-Llama-3-8B-Instruct"
    base_save_dir = Path(__file__).parent.parent / "models" / "llama-3-8b-base"
    base_save_dir.mkdir(parents=True, exist_ok=True)
    
    snapshot_download(
        repo_id=base_model,
        local_dir=str(base_save_dir),
        local_dir_use_symlinks=False,
        resume_download=True,
        token=hf_token
    )
    
    print("\n✅ Base model downloaded!")
    
    # Download 2: Food/Nutrition LoRA Adapter
    print("\n" + "=" * 70)
    print("📥 STEP 2/2: Downloading Food/Nutrition LoRA Adapter (~100MB)")
    print("=" * 70)
    print("⏳ This will be quick...\n")
    
    adapter_model = "fortymiles/Llama-3-8B-sft-lora-food-nutrition-10-epoch"
    adapter_save_dir = Path(__file__).parent.parent / "models" / "llama-3-food-nutrition-adapter"
    adapter_save_dir.mkdir(parents=True, exist_ok=True)
    
    snapshot_download(
        repo_id=adapter_model,
        local_dir=str(adapter_save_dir),
        local_dir_use_symlinks=False,
        resume_download=True,
        token=hf_token
    )
    
    print("\n✅ LoRA adapter downloaded!")
    
    # Success message
    print("\n" + "=" * 70)
    print("✅ COMPLETE MODEL DOWNLOADED - FULLY OFFLINE!")
    print("=" * 70)
    print(f"\n📁 Base model: {base_save_dir}")
    print(f"   Size: ~15.9GB")
    print(f"\n📁 LoRA adapter: {adapter_save_dir}")
    print(f"   Size: ~100MB")
    print(f"\n📊 Total size: ~16GB")
    print(f"\n📋 Next steps:")
    print(f"   1. Zip both folders (optional - for easier upload):")
    print(f"      - {base_save_dir.name}")
    print(f"      - {adapter_save_dir.name}")
    print(f"   2. Upload to Google Drive")
    print(f"   3. In Colab, extract and use local paths")
    print(f"\n💡 Colab paths (update in colab_model_server_local.py):")
    print(f"      base_model = '/content/llama-3-8b-base'")
    print(f"      adapter_path = '/content/llama-3-food-nutrition-adapter'")
    print(f"\n🎯 Result: 100% offline - no internet needed in Colab!")
    print(f"   4-bit quantization will still work with BitsAndBytes")
    print(f"   Memory usage: ~6GB VRAM")
    print("\n")
    
except Exception as e:
    print(f"\n❌ Download failed: {e}")
    print("\n💡 Troubleshooting:")
    print("   1. Check your HuggingFace token is valid")
    print("   2. Accept Llama-3 license:")
    print("      https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct")
    print("   3. Check internet connection and disk space (need 20GB free)")
    print("   4. Try running again - downloads resume from where they stopped")
