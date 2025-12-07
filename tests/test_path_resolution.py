from service.api import resolve_pdf_path

# Test path resolution
test_paths = [
    r"outputs\raw\1\PROBIOTIC RICH DIET\probiotic rich diet for male north indian vegeterian light active overweight.txt",
    r"d:\Documents\Diet plan\outputs\raw\1\SKIN DETOX\skin detox male north indian non veg sedentary overweight.txt"
]

for path in test_paths:
    resolved = resolve_pdf_path(path)
    print(f"\nOriginal: {path}")
    print(f"Resolved: {resolved}")
    
    # Check if file exists
    import os
    exists = os.path.exists(resolved)
    print(f"Exists: {exists}")
