# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['/Users/yuclaw/.openclaw/workspace/合同对比助手/src/main.py'],
    pathex=['/Users/yuclaw/.openclaw/workspace/合同对比助手/src'],
    binaries=[],
    datas=[('version.json', '.')],
    hiddenimports=['core', 'core.doc_comparator', 'ui', 'ui.main_window', 'utils', 'utils.logger', 'utils.error_handler', 'utils.pdf_handler', 'utils.updater', 'utils.styles', 'docx', 'openpyxl', 'diff_match_patch', 'pdfplumber', 'pdf2docx', 'PyMuPDF'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'scipy', 'pytest', 'cv2', 'opencv_python_headless', 'PIL', 'pillow'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='合同对比助手',
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
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='合同对比助手',
)
app = BUNDLE(
    coll,
    name='合同对比助手.app',
    icon=None,
    bundle_identifier=None,
)
