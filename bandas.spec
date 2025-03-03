# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['bandas.py'],
    pathex=[],
    binaries=[],
    datas=[('assets/icon_generar.png', '.'), ('assets/icon_guardar.png', '.'), ('assets/icon_reset.png', '.')],
    hiddenimports=['matplotlib', 'PIL'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='bandas',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets\\Module30px.ico'],
)
