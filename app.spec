# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

app = Analysis(
    ['src\\app.py', '.\\app.spec'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=["MySQLdb"],
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
    ['src/updater_app.py'],
    pathex=[],
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
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
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
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
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

