import os
from pathlib import Path

# Define all directories
directories = [
    "src/ui/dialogs",
    "src/ui/widgets",
    "src/ui/resources",
    "src/core",
    "src/ai/models",
    "src/database",
    "src/utils",
    "config",
    "docs",
    "tests",
    "scripts",
    "sample_data",
    "build"
]

# Create directories
for dir_path in directories:
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    
# Create __init__.py files
init_files = [
    "src/__init__.py",
    "src/ui/__init__.py",
    "src/ui/dialogs/__init__.py",
    "src/ui/widgets/__init__.py",
    "src/core/__init__.py",
    "src/ai/__init__.py",
    "src/ai/models/__init__.py",
    "src/database/__init__.py",
    "src/utils/__init__.py",
    "tests/__init__.py"
]

for file_path in init_files:
    Path(file_path).touch()

print("✅ Project structure created successfully!")