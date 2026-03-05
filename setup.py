#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合同对比助手 - macOS py2app 打包配置
"""

from setuptools import setup
import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

APP = ['src/main.py']
DATA_FILES = [
    'version.json',
]

OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'icon.icns',
    'plist': {
        'CFBundleName': '合同对比助手',
        'CFBundleDisplayName': '合同对比助手',
        'CFBundleIdentifier': 'com.yuclaw.contractdiff',
        'CFBundleVersion': '1.2.3',
        'CFBundleShortVersionString': '1.2.3',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.15',
        'NSLocationWhenInUseUsageDescription': 'This app does not use location services',
        'NSCameraUsageDescription': 'This app does not use camera',
        'NSMicrophoneUsageDescription': 'This app does not use microphone',
    },
    'includes': [
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'docx',
        'openpyxl',
        'diff_match_patch',
        'pdfplumber',
        'pdf2docx',
    ],
    'packages': [
        'core',
        'ui',
        'utils',
        'docx',
        'openpyxl',
        'lxml',
    ],
    'excludes': [
        'tkinter',
        'matplotlib',
        'scipy',
        'numpy',  # 不需要
        'PIL',  # 不需要
        'cv2',  # 不需要
        'pytest',
    ],
    'site_packages': True,
    'resources': ['src'],
}

setup(
    name='合同对比助手',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
