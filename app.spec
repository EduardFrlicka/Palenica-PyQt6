# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

# Both entry points live in src/ and import their neighbours flatly
# (import config, import db), so src/ has to be on the analysis path.
SRC = 'src'

app = Analysis(
    [os.path.join(SRC, 'app.py')],
    pathex=[SRC],
    binaries=[],
    datas=[],
    # db.turso_dialect is only ever reached through SQLAlchemy's string-keyed
    # dialect registry, so PyInstaller cannot see it by following imports.
    hiddenimports=["libsql", "db.turso_dialect"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

updater = Analysis(
    [os.path.join(SRC, 'updater_app.py')],
    pathex=[SRC],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

MERGE((app, 'app', 'app'), (updater, 'updater', 'updater'))

app_pyz = PYZ(app.pure, app.zipped_data, cipher=block_cipher)
updater_pyz = PYZ(updater.pure, updater.zipped_data, cipher=block_cipher)

app_exe = EXE(
    app_pyz,
    app.dependencies,
    app.scripts,
    [],
    exclude_binaries=True,
    name='Palenica',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

updater_exe = EXE(
    updater_pyz,
    updater.dependencies,
    updater.scripts,
    [],
    exclude_binaries=True,
    name='updater',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    app_exe,
    app.binaries,
    app.zipfiles,
    app.datas,
    updater_exe,
    updater.binaries,
    updater.zipfiles,
    updater.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)

