#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口界面 v1.2
集成日志、异常处理、PDF 支持、自动更新
"""

import os
import sys
import platform
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QProgressBar,
    QCheckBox, QGroupBox, QMenuBar, QMenu,
    QStatusBar, QMessageBox, QFrame, QTextEdit, QDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QAction


def get_system_font():
    """获取系统字体（跨平台兼容）"""
    system = platform.system()
    if system == "Darwin":  # macOS
        return "PingFang SC"
    elif system == "Windows":
        return "Microsoft YaHei"
    else:  # Linux 等其他系统
        return "WenQuanYi Micro Hei"

from core.doc_comparator import DocumentComparator
from utils.styles import STYLESHEET
from utils.logger import logger
from utils.error_handler import (
    FileLoadError, FileFormatError, CompareError, 
    OutputError, get_friendly_error_message
)
from utils.pdf_handler import DocumentLoader
from utils.updater import updater


class CompareWorker(QThread):
    """对比工作线程"""
    progress = pyqtSignal(int, str)  # 进度百分比，当前步骤
    result = pyqtSignal(dict)  # 对比结果
    error = pyqtSignal(str)  # 错误信息
    
    def __init__(self, file_x, file_y, output_options):
        super().__init__()
        self.file_x = file_x
        self.file_y = file_y
        self.output_options = output_options
        self.temp_files = []
    
    def run(self):
        try:
            logger.info(f"开始对比任务：{os.path.basename(self.file_x)} vs {os.path.basename(self.file_y)}")
            
            comparator = DocumentComparator()
            
            self.progress.emit(10, "正在加载文档...")
            
            # 使用统一文档加载器（支持 Word 和 PDF）
            loader = DocumentLoader()
            file_x_path, is_temp_x = loader.load_document(self.file_x)
            file_y_path, is_temp_y = loader.load_document(self.file_y)
            
            if is_temp_x:
                self.temp_files.append(file_x_path)
            if is_temp_y:
                self.temp_files.append(file_y_path)
            
            comparator.load_documents(file_x_path, file_y_path)
            logger.debug("文档加载成功")
            
            self.progress.emit(30, "正在分析段落结构...")
            comparator.analyze_structure()
            logger.debug("结构分析完成")
            
            self.progress.emit(50, "正在对比文字差异...")
            comparator.compare_content()
            logger.debug(f"对比完成，发现 {len(comparator.changes)} 处改动")
            
            self.progress.emit(70, "正在识别关键改动...")
            comparator.identify_changes()
            logger.debug("改动识别完成")
            
            self.progress.emit(85, "正在生成结果文档...")
            result_path = comparator.generate_output(self.output_options)
            logger.info(f"结果文档已生成：{result_path}")
            
            # 清理临时文件
            for temp_file in self.temp_files:
                loader.cleanup_temp_file(temp_file)
            
            self.progress.emit(100, "对比完成")
            self.result.emit({
                'path': result_path,
                'stats': comparator.get_stats()
            })
            
        except (FileLoadError, FileFormatError, CompareError, OutputError) as e:
            logger.error(f"对比失败：{e}", exc_info=True)
            self.error.emit(get_friendly_error_message(e))
        except Exception as e:
            logger.critical(f"未预期的错误：{e}", exc_info=True)
            self.error.emit(f"发生未知错误：{str(e)}\n\n已记录到日志文件，请联系技术支持。")


class ChangelogDialog(QDialog):
    """更新说明对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("更新说明")
        self.setMinimumSize(700, 500)
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # 标题
        font_name = get_system_font()
        title = QLabel("合同对比助手 - 版本更新日志")
        title.setFont(QFont(font_name, 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 更新日志文本框
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont(font_name, 10))
        layout.addWidget(self.text_edit)
        
        # 加载更新日志
        self.load_changelog()
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.setFixedHeight(40)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)
    
    def load_changelog(self):
        """加载更新日志"""
        try:
            changelog = updater.get_changelog()
            # 将 Markdown 转换为简单 HTML 显示
            html = changelog.replace('# ', '<h2>')
            html = html.replace('## ', '<h3>')
            html = html.replace('### ', '<h4>')
            html = html.replace('**', '<b>').replace('</b>', '</b>')
            html = html.replace('\n', '<br>')
            self.text_edit.setHtml(html)
        except Exception as e:
            logger.error(f"加载更新日志失败：{e}")
            self.text_edit.setHtml("<p>加载更新日志失败，请稍后重试。</p>")


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.file_x = None
        self.file_y = None
        self.worker = None
        self.doc_loader = DocumentLoader()
        self.version = self._get_version()
        
        logger.info("=" * 50)
        logger.info(f"合同对比助手 v{self.version} 启动")
        logger.info("=" * 50)
        
        self.init_ui()
        self.apply_style()
        
        # 启动后检查更新
        self.check_update_on_startup()
    
    def _get_version(self):
        """从 version.json 读取版本号"""
        try:
            import json
            import os
            import sys
            for base in [os.path.dirname(sys.argv[0]), os.path.dirname(os.path.abspath(__file__))]:
                version_file = os.path.join(base, '..', 'version.json')
                if os.path.exists(version_file):
                    with open(version_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        return data.get('version', '1.0')
                # 检查打包后环境
                if hasattr(sys, '_MEIPASS'):
                    version_file = os.path.join(sys._MEIPASS, 'version.json')
                    if os.path.exists(version_file):
                        with open(version_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            return data.get('version', '1.0')
        except Exception:
            pass
        return '1.0'
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle(f"合同对比助手 v{self.version}")
        self.setMinimumSize(900, 700)
        self.resize(1000, 750)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 文件选择区域
        file_group = self.create_file_selection_group()
        main_layout.addWidget(file_group)
        
        # 输出选项区域
        output_group = self.create_output_options_group()
        main_layout.addWidget(output_group)
        
        # 保存设置区域
        save_group = self.create_save_settings_group()
        main_layout.addWidget(save_group)
        
        # 对比按钮
        font_name = get_system_font()
        self.compare_btn = QPushButton("开 始 对 比")
        self.compare_btn.setFixedHeight(50)
        self.compare_btn.setFont(QFont(font_name, 12, QFont.Weight.Bold))
        self.compare_btn.clicked.connect(self.start_compare)
        main_layout.addWidget(self.compare_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 进度区域（初始隐藏）
        self.progress_group = self.create_progress_group()
        self.progress_group.hide()
        main_layout.addWidget(self.progress_group)
        
        # 状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("状态：就绪")
        
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件 (&F)")
        
        open_x_action = QAction("选择原文档 (&X)", self)
        open_x_action.setShortcut("Ctrl+X")
        open_x_action.triggered.connect(lambda: self.select_file('X'))
        file_menu.addAction(open_x_action)
        
        open_y_action = QAction("选择修改文档 (&Y)", self)
        open_y_action.setShortcut("Ctrl+Y")
        open_y_action.triggered.connect(lambda: self.select_file('Y'))
        file_menu.addAction(open_y_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出 (&Q)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 工具菜单
        tool_menu = menubar.addMenu("工具 (&T)")
        
        check_update_action = QAction("检查更新 (&U)", self)
        check_update_action.triggered.connect(self.manual_check_update)
        tool_menu.addAction(check_update_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助 (&H)")
        
        changelog_action = QAction("更新说明 (&C)", self)
        changelog_action.triggered.connect(self.show_changelog)
        help_menu.addAction(changelog_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("关于 (&A)", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_file_selection_group(self):
        """创建文件选择区域"""
        group = QGroupBox("文件选择")
        layout = QVBoxLayout()
        
        # 文件选择行
        file_layout = QHBoxLayout()
        file_layout.setSpacing(30)
        
        font_name = get_system_font()
        # 原文档 X
        x_layout = QVBoxLayout()
        x_label = QLabel("原文档 (X)")
        x_label.setFont(QFont(font_name, 10, QFont.Weight.Bold))
        x_layout.addWidget(x_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.btn_select_x = QPushButton("选择文件...")
        self.btn_select_x.setFixedHeight(100)
        self.btn_select_x.clicked.connect(lambda: self.select_file('X'))
        x_layout.addWidget(self.btn_select_x)
        
        self.label_file_x = QLabel("未选择文件")
        self.label_file_x.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_file_x.setStyleSheet("color: #666666; padding: 5px;")
        x_layout.addWidget(self.label_file_x)
        
        file_layout.addLayout(x_layout)
        
        # 修改文档 Y
        y_layout = QVBoxLayout()
        y_label = QLabel("修改文档 (Y)")
        y_label.setFont(QFont(font_name, 10, QFont.Weight.Bold))
        y_layout.addWidget(y_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.btn_select_y = QPushButton("选择文件...")
        self.btn_select_y.setFixedHeight(100)
        self.btn_select_y.clicked.connect(lambda: self.select_file('Y'))
        y_layout.addWidget(self.btn_select_y)
        
        self.label_file_y = QLabel("未选择文件")
        self.label_file_y.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_file_y.setStyleSheet("color: #666666; padding: 5px;")
        y_layout.addWidget(self.label_file_y)
        
        file_layout.addLayout(y_layout)
        layout.addLayout(file_layout)
        group.setLayout(layout)
        
        return group
    
    def create_output_options_group(self):
        """创建输出选项区域"""
        group = QGroupBox("输出选项")
        layout = QHBoxLayout()
        layout.setSpacing(30)
        
        self.chk_detail_list = QCheckBox("详细改动列表")
        self.chk_detail_list.setChecked(True)
        layout.addWidget(self.chk_detail_list)
        
        self.chk_report = QCheckBox("对比报告 (Excel)")
        self.chk_report.setChecked(True)
        layout.addWidget(self.chk_report)
        
        layout.addStretch()
        group.setLayout(layout)
        
        return group
    
    def create_save_settings_group(self):
        """创建保存设置区域"""
        group = QGroupBox("保存设置")
        layout = QHBoxLayout()
        
        self.label_save_path = QLabel("保存位置：")
        layout.addWidget(self.label_save_path)
        
        # 跨平台路径显示
        if platform.system() == "Windows":
            default_path = "C:\\Users\\...\\Documents\\合同对比结果_时间戳.docx"
        else:
            default_path = "~/Documents/合同对比结果_时间戳.docx"
        
        self.edit_save_path = QLabel(default_path)
        self.edit_save_path.setStyleSheet("color: #333333;")
        layout.addWidget(self.edit_save_path, stretch=1)
        
        self.btn_browse = QPushButton("更改目录...")
        self.btn_browse.clicked.connect(self.browse_save_path)
        layout.addWidget(self.btn_browse)
        
        group.setLayout(layout)
        
        return group
    
    def create_progress_group(self):
        """创建进度区域"""
        group = QGroupBox("对比进度")
        layout = QVBoxLayout()
        
        font_name = get_system_font()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(25)
        layout.addWidget(self.progress_bar)
        
        self.label_progress_step = QLabel("准备中...")
        self.label_progress_step.setFont(QFont(font_name, 10))
        layout.addWidget(self.label_progress_step)
        
        # 进度详情
        self.progress_details = QFrame()
        self.progress_details.setFrameStyle(QFrame.Shape.StyledPanel)
        details_layout = QVBoxLayout(self.progress_details)
        
        self.steps = [
            ("文档加载与解析", QLabel("○ 文档加载与解析")),
            ("段落级对比", QLabel("○ 段落级对比")),
            ("句子级差异识别", QLabel("○ 句子级差异识别")),
            ("改动分类与标注", QLabel("○ 改动分类与标注")),
            ("结果文档生成", QLabel("○ 结果文档生成")),
        ]
        
        for _, label in self.steps:
            label.setFont(QFont(font_name, 9))
            details_layout.addWidget(label)
        
        layout.addWidget(self.progress_details)
        
        # 改动统计
        self.label_stats = QLabel("")
        self.label_stats.setFont(QFont("Microsoft YaHei", 9))
        self.label_stats.setStyleSheet("color: #666666;")
        layout.addWidget(self.label_stats)
        
        # 取消按钮
        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.setFixedWidth(100)
        self.btn_cancel.clicked.connect(self.cancel_compare)
        layout.addWidget(self.btn_cancel, alignment=Qt.AlignmentFlag.AlignCenter)
        
        group.setLayout(layout)
        
        return group
    
    def apply_style(self):
        """应用样式"""
        self.setStyleSheet(STYLESHEET)
    
    def select_file(self, file_type):
        """选择文件"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "选择文档",
                "",
                "Word/PDF 文档 (*.docx *.pdf);;Word 文档 (*.docx);;PDF 文档 (*.pdf);;所有文件 (*.*)"
            )
            
            if file_path:
                logger.info(f"选择文件 ({file_type}): {file_path}")
                
                if file_type == 'X':
                    self.file_x = file_path
                    file_name = os.path.basename(file_path)
                    file_size = os.path.getsize(file_path) / 1024 / 1024
                    file_ext = os.path.splitext(file_path)[1].upper()
                    self.label_file_x.setText(f"{file_name}\n({file_size:.1f} MB, {file_ext})")
                    self.label_file_x.setStyleSheet("color: #1E3A5F; font-weight: bold; padding: 5px;")
                else:
                    self.file_y = file_path
                    file_name = os.path.basename(file_path)
                    file_size = os.path.getsize(file_path) / 1024 / 1024
                    file_ext = os.path.splitext(file_path)[1].upper()
                    self.label_file_y.setText(f"{file_name}\n({file_size:.1f} MB, {file_ext})")
                    self.label_file_y.setStyleSheet("color: #1E3A5F; font-weight: bold; padding: 5px;")
                
                self.check_ready()
                
        except Exception as e:
            logger.error(f"选择文件失败：{e}", exc_info=True)
            QMessageBox.critical(self, "错误", f"选择文件时发生错误：{str(e)}")
    
    def browse_save_path(self):
        """浏览保存路径"""
        path = QFileDialog.getExistingDirectory(
            self,
            "选择保存目录",
            os.path.expanduser("~/Documents")
        )
        if path:
            # 跨平台路径分隔符
            separator = "\\" if platform.system() == "Windows" else "/"
            self.edit_save_path.setText(path + separator + "合同对比结果_时间戳.docx")
    
    def check_ready(self):
        """检查是否准备好对比"""
        ready = self.file_x is not None and self.file_y is not None
        self.compare_btn.setEnabled(ready)
        if ready:
            self.statusBar.showMessage("状态：已就绪，可以开始对比")
        else:
            self.statusBar.showMessage("状态：请选择两个文档")
    
    def start_compare(self):
        """开始对比"""
        try:
            if not self.file_x or not self.file_y:
                QMessageBox.warning(self, "警告", "请先选择两个文档")
                return
            
            # 获取输出选项
            save_path_text = self.edit_save_path.text()
            # 处理占位符路径
            if '...' in save_path_text or not save_path_text:
                save_path = os.path.expanduser("~/Documents")
            else:
                save_path = os.path.dirname(save_path_text) or os.path.expanduser("~/Documents")
            
            # 确保目录存在
            os.makedirs(save_path, exist_ok=True)
            
            output_options = {
                'detail_list': self.chk_detail_list.isChecked(),
                'report': self.chk_report.isChecked(),
                'save_path': save_path
            }
            
            logger.info(f"开始对比，选项：{output_options}")
            
            # 禁用界面
            self.set_ui_enabled(False)
            
            # 显示进度区域
            self.progress_group.show()
            
            # 创建工作线程
            self.worker = CompareWorker(self.file_x, self.file_y, output_options)
            self.worker.progress.connect(self.on_progress)
            self.worker.result.connect(self.on_result)
            self.worker.error.connect(self.on_error)
            self.worker.start()
            
        except Exception as e:
            logger.error(f"启动对比失败：{e}", exc_info=True)
            QMessageBox.critical(self, "错误", f"启动对比失败：{str(e)}")
            self.set_ui_enabled(True)
    
    def cancel_compare(self):
        """取消对比"""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.set_ui_enabled(True)
            self.progress_group.hide()
            self.statusBar.showMessage("状态：已取消")
            logger.info("用户取消对比")
    
    def on_progress(self, value, step):
        """更新进度"""
        self.progress_bar.setValue(value)
        self.label_progress_step.setText(step)
        
        # 更新步骤状态
        steps_map = {
            10: 0, 30: 1, 50: 2, 70: 3, 85: 4
        }
        for threshold, idx in steps_map.items():
            if value >= threshold:
                label = self.steps[idx][1]
                label.setText(f"● {self.steps[idx][0]}")
                label.setStyleSheet("color: #1E3A5F; font-weight: bold;")
    
    def on_result(self, result):
        """对比完成"""
        self.set_ui_enabled(True)
        self.progress_group.hide()
        
        stats = result['stats']
        total = sum(stats.values())
        
        logger.info(f"对比完成，共发现 {total} 处改动")
        
        # 显示完成消息
        msg = f"对比完成！\n\n共发现 {total} 处改动：\n"
        msg += f"  文字新增：{stats.get('additions', 0)} 处\n"
        msg += f"  文字删除：{stats.get('deletions', 0)} 处\n"
        msg += f"  文字修改：{stats.get('modifications', 0)} 处\n"
        msg += f"  数字变化：{stats.get('number_changes', 0)} 处\n\n"
        msg += f"结果已保存至：\n{result['path']}"
        
        QMessageBox.information(self, "对比完成", msg)
        
        # 自动打开结果文档
        self._open_result_file(result['path'])
        
        self.statusBar.showMessage(f"状态：对比完成，共发现 {total} 处改动")
    
    def _open_result_file(self, file_path):
        """自动打开结果文件"""
        try:
            import subprocess
            logger.info(f"正在打开结果文件：{file_path}")
            subprocess.run(['open', file_path], check=True, capture_output=True)
            logger.info("结果文件已打开")
        except Exception as e:
            logger.warning(f"自动打开文件失败：{e}")
    
    def on_error(self, error_msg):
        """处理错误"""
        self.set_ui_enabled(True)
        self.progress_group.hide()
        logger.error(f"对比错误：{error_msg}")
        QMessageBox.critical(self, "错误", error_msg)
        self.statusBar.showMessage("状态：发生错误")
    
    def set_ui_enabled(self, enabled):
        """设置界面启用状态"""
        self.btn_select_x.setEnabled(enabled)
        self.btn_select_y.setEnabled(enabled)
        self.compare_btn.setEnabled(enabled and (self.file_x is not None) and (self.file_y is not None))
        self.btn_browse.setEnabled(enabled)
        self.btn_cancel.setEnabled(not enabled)
    
    def check_update_on_startup(self):
        """启动时检查更新"""
        try:
            if updater.should_check_update():
                logger.info("启动时检查更新...")
                update_info = updater.check_for_updates()
                
                if update_info.get('has_update'):
                    self.show_update_notification(update_info)
        except Exception as e:
            logger.warning(f"启动时检查更新失败：{e}")
    
    def manual_check_update(self):
        """手动检查更新"""
        try:
            self.statusBar.showMessage("正在检查更新...")
            update_info = updater.check_for_updates()
            
            if update_info.get('has_update'):
                self.show_update_notification(update_info)
            else:
                QMessageBox.information(
                    self,
                    "检查更新",
                    f"当前已是最新版本 (v{updater.current_version})"
                )
            
            self.statusBar.showMessage("状态：就绪")
        except Exception as e:
            logger.error(f"检查更新失败：{e}", exc_info=True)
            QMessageBox.warning(
                self,
                "检查更新",
                f"检查更新失败：{str(e)}\n\n请稍后重试。"
            )
            self.statusBar.showMessage("状态：就绪")
    
    def show_update_notification(self, update_info):
        """显示更新通知"""
        version = update_info.get('version', '')
        changes = update_info.get('changes', [])
        download_url = update_info.get('download_url', '')
        
        msg = f"发现新版本 v{version}！\n\n"
        msg += "更新内容：\n"
        for change in changes[:5]:  # 最多显示 5 条
            msg += f"  • {change}\n"
        
        if len(changes) > 5:
            msg += f"  ... 共 {len(changes)} 项更新\n"
        
        msg += "\n是否立即下载？"
        
        reply = QMessageBox.question(
            self,
            "发现新版本",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            import webbrowser
            webbrowser.open(download_url)
            logger.info(f"用户选择下载更新：{download_url}")
    
    def show_changelog(self):
        """显示更新说明"""
        logger.info("用户查看更新说明")
        dialog = ChangelogDialog(self)
        dialog.exec()
    
    def show_about(self):
        """显示关于对话框"""
        # 从 version.json 读取版本号和平台信息
        version = "1.0.0"
        platform_info = ""
        try:
            import json
            import os
            import sys
            for base in [os.path.dirname(sys.argv[0]), os.path.dirname(os.path.abspath(__file__))]:
                version_file = os.path.join(base, '..', 'version.json')
                if os.path.exists(version_file):
                    with open(version_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        version = data.get('version', '1.0.0')
                        platform_info = data.get('platform', 'macOS')
                    break
                if hasattr(sys, '_MEIPASS'):
                    version_file = os.path.join(sys._MEIPASS, 'version.json')
                    if os.path.exists(version_file):
                        with open(version_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            version = data.get('version', '1.0.0')
                            platform_info = data.get('platform', 'macOS')
                        break
        except Exception:
            pass
        
        QMessageBox.about(
            self,
            "关于合同对比助手",
            f"合同对比助手 v{version}\n{platform_info} 版本\n\n"
            "一款专业的合同文档差异对比工具\n\n"
            "功能特点：\n"
            "• 自动识别文字增删改\n"
            "• 详细改动列表输出（第 X 段）\n"
            "• 生成 Excel 对比报告\n"
            "• 支持 Word (.docx) 和 PDF 格式\n"
            "• 日志记录与异常处理\n"
            "• 自动打开结果文档\n\n"
            "玉哥与他的虾\n"
            "版权所有 © 2026"
        )
