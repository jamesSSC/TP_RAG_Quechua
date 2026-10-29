# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('data/fragmentos_v3.jsonl', 'data'), ('data/traduccion_en_es.json', 'data'), ('interfaz', 'interfaz'), ('modelos', 'modelos'), ('db', 'db')]
binaries = []
# `in` es palabra reservada: estos paquetes se cargan con importlib y PyInstaller no los ve.
hiddenimports = [
    'adapters.in', 'adapters.in.rest', 'adapters.in.rest.dependencias',
    'adapters.in.rest.esquemas', 'adapters.in.rest.consultas_controller',
    'adapters.in.rest.corpus_controller', 'adapters.in.rest.fuentes_controller',
    'adapters.in.rest.historial_controller', 'adapters.in.rest.sistema_controller',
    'application.ports.in', 'application.ports.in.consultar_corpus_port',
    'application.ports.in.ingestar_documento_port', 'application.ports.in.gestionar_fuentes_port',
    'application.ports.in.consultar_historial_port', 'application.ports.in.reindexar_corpus_port',
    'uvicorn.logging', 'uvicorn.protocols.http.auto', 'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan.on', 'sqlalchemy.dialects.sqlite',
]
tmp_ret = collect_all('sklearn')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('scipy')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('numpy')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['ejecutable.py'],
    pathex=['src'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='QuechuaWankaWeb',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
