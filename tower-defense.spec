# -*- mode: python ; coding: utf-8 -*-
"""Spécification PyInstaller pour construire l'exécutable du jeu.

Construit un exécutable fenêtré autonome nommé « TowerDefense » qui embarque
la ressource Pyxel (assets/theme.pyxres). Sur macOS, un bundle .app est aussi
généré.

Usage :
    pyinstaller tower-defense.spec
"""

block_cipher = None

a = Analysis(
    ["app.py"],
    pathex=["."],
    binaries=[],
    datas=[("assets/theme.pyxres", "assets")],
    # Pyxel importe certains modules de la bibliothèque standard dynamiquement ;
    # PyInstaller ne les détecte pas automatiquement.
    hiddenimports=["tower_defense", "inspect", "glob", "platform", "json"],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="TowerDefense",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False,          # application fenêtrée (pas de console)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Bundle macOS (.app) — ignoré sur les autres plateformes.
app = BUNDLE(
    exe,
    name="TowerDefense.app",
    icon=None,
    bundle_identifier="com.antoninche.towerdefense",
    info_plist={
        "CFBundleName": "Tower Defense",
        "CFBundleDisplayName": "Tower Defense",
        "CFBundleShortVersionString": "1.0.0",
        "NSHighResolutionCapable": True,
    },
)
