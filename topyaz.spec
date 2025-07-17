# -*- mode: python ; coding: utf-8 -*-
# this_file: topyaz.spec

import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Define the application name
app_name = "topyaz"

# Define the main script
main_script = "src/topyaz/__main__.py"

# Define data files to include
datas = [
    # Include the entire topyaz package
    ("src/topyaz", "topyaz"),
    # Include any configuration files
    ("src/topyaz/data", "topyaz/data") if os.path.exists("src/topyaz/data") else None,
]

# Filter out None entries
datas = [d for d in datas if d is not None]

# Define hidden imports
hiddenimports = [
    "topyaz",
    "topyaz.cli",
    "topyaz.core",
    "topyaz.core.config",
    "topyaz.core.errors",
    "topyaz.core.types",
    "topyaz.execution",
    "topyaz.execution.local",
    "topyaz.execution.base",
    "topyaz.products",
    "topyaz.products.base",
    "topyaz.products.gigapixel",
    "topyaz.products.gigapixel.api",
    "topyaz.products.gigapixel.params",
    "topyaz.products.video_ai",
    "topyaz.products.video_ai.api", 
    "topyaz.products.video_ai.params",
    "topyaz.products.photo_ai",
    "topyaz.products.photo_ai.api",
    "topyaz.products.photo_ai.params",
    "topyaz.products.photo_ai.batch",
    "topyaz.products.photo_ai.preferences",
    "topyaz.system",
    "topyaz.system.environment",
    "topyaz.system.gpu",
    "topyaz.system.memory",
    "topyaz.system.paths",
    "topyaz.system.preferences",
    "topyaz.utils",
    "topyaz.utils.logging",
    "topyaz.utils.validation",
    # External dependencies
    "fire",
    "paramiko",
    "fabric",
    "pyyaml",
    "tqdm",
    "psutil",
    "loguru",
    "rich",
    "typing_extensions",
    "PIL",
    "PIL.Image",
]

# Define binary excludes
excludes = [
    "tkinter",
    "unittest",
    "test",
    "tests",
    "matplotlib",
    "numpy",
    "scipy",
    "pandas",
    "jupyter",
    "ipython",
    "notebook",
]

# Analysis configuration
a = Analysis(
    [main_script],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicates
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Create the executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one
)

# macOS app bundle (optional)
if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name=f"{app_name}.app",
        icon=None,  # Add icon path here if you have one
        bundle_identifier=f"com.twardoch.{app_name}",
        info_plist={
            "CFBundleDisplayName": "Topyaz",
            "CFBundleIdentifier": "com.twardoch.topyaz",
            "CFBundleName": "Topyaz",
            "CFBundleVersion": "1.0.0",
            "CFBundleShortVersionString": "1.0.0",
            "NSHumanReadableCopyright": "Copyright © 2024 Adam Twardoch. All rights reserved.",
            "LSApplicationCategoryType": "public.app-category.developer-tools",
        },
    )