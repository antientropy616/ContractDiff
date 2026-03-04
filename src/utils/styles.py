#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用样式表 - 法律严肃风格
"""

STYLESHEET = """
/* 主窗口 */
QMainWindow {
    background-color: #F5F5F5;
}

/* 分组框 */
QGroupBox {
    font-size: 11pt;
    font-weight: bold;
    color: #1E3A5F;
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 15px;
    background-color: #FFFFFF;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 15px;
    padding: 0 8px;
    color: #1E3A5F;
}

/* 按钮 */
QPushButton {
    background-color: #1E3A5F;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 10px 25px;
    font-size: 10pt;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #2C4A6E;
}

QPushButton:pressed {
    background-color: #162D4A;
}

QPushButton:disabled {
    background-color: #CCCCCC;
    color: #666666;
}

/* 复选框 */
QCheckBox {
    font-size: 10pt;
    color: #333333;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #CCCCCC;
    border-radius: 3px;
    background-color: white;
}

QCheckBox::indicator:checked {
    background-color: #1E3A5F;
    border-color: #1E3A5F;
}

/* 进度条 */
QProgressBar {
    border: 1px solid #CCCCCC;
    border-radius: 3px;
    text-align: center;
    background-color: #F0F0F0;
    color: #333333;
    font-weight: bold;
}

QProgressBar::chunk {
    background-color: #1E3A5F;
    border-radius: 2px;
}

/* 标签 */
QLabel {
    color: #333333;
    font-size: 10pt;
}

/* 状态栏 */
QStatusBar {
    background-color: #F0F0F0;
    border-top: 1px solid #CCCCCC;
    color: #666666;
    font-size: 9pt;
}

/* 菜单栏 */
QMenuBar {
    background-color: #FFFFFF;
    border-bottom: 1px solid #CCCCCC;
    color: #333333;
    font-size: 10pt;
}

QMenuBar::item {
    padding: 5px 12px;
    background-color: transparent;
}

QMenuBar::item:selected {
    background-color: #E8E8E8;
}

QMenuBar::item:pressed {
    background-color: #D0D0D0;
}

/* 菜单 */
QMenu {
    background-color: #FFFFFF;
    border: 1px solid #CCCCCC;
    color: #333333;
}

QMenu::item {
    padding: 6px 30px 6px 25px;
}

QMenu::item:selected {
    background-color: #1E3A5F;
    color: white;
}

QMenu::separator {
    height: 1px;
    background-color: #CCCCCC;
    margin: 4px 10px;
}

/* 对话框 */
QMessageBox {
    background-color: #FFFFFF;
}

QMessageBox QLabel {
    color: #333333;
    font-size: 10pt;
}

QMessageBox QPushButton {
    min-width: 80px;
    padding: 8px 20px;
}

/* 文件对话框 */
QFileDialog {
    background-color: #FFFFFF;
}

/* 滚动条 */
QScrollBar:vertical {
    background-color: #F0F0F0;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #CCCCCC;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #AAAAAA;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

/* 工具提示 */
QToolTip {
    background-color: #1E3A5F;
    color: white;
    border: none;
    padding: 5px 10px;
    border-radius: 3px;
    font-size: 9pt;
}

/* 框架 */
QFrame {
    background-color: #FFFFFF;
    border: 1px solid #EEEEEE;
    border-radius: 4px;
    padding: 10px;
}

/* 输入框（如果后续需要） */
QLineEdit {
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    padding: 8px 12px;
    background-color: white;
    color: #333333;
    font-size: 10pt;
}

QLineEdit:focus {
    border-color: #1E3A5F;
}

QLineEdit:disabled {
    background-color: #F5F5F5;
    color: #999999;
}
"""
