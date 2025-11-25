# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None
added_files = [
    ("src/bsdd_gui/resources", "bsdd_gui/resources"),
    ("src/bsdd_gui/plugins", "bsdd_gui/plugins"),
    (r'.venv/Lib/site-packages/ifctester/ids.xsd', 'ifctester'),
]

hi = collect_submodules("bsdd_json")
a = Analysis(
    ["src/bsdd_gui/__main__.py"],
    pathex=["src"],
    binaries=[],
    datas=added_files,
    hiddenimports=hi,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="BSDD-Toolkit",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="src/bsdd_gui/resources/icons/icon.ico")
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=f"BSDD-Toolkit")
