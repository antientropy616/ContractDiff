#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异常处理模块
提供友好的错误提示和异常分类
"""

from utils.logger import logger


class ContractDiffError(Exception):
    """合同对比基础异常"""
    def __init__(self, message, error_code="UNKNOWN"):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        logger.error(f"[{error_code}] {message}")


class FileLoadError(ContractDiffError):
    """文件加载错误"""
    def __init__(self, message, file_path=None):
        error_code = "FILE_LOAD_ERROR"
        if file_path:
            message = f"无法加载文件：{file_path}\n{message}"
        super().__init__(message, error_code)


class FileFormatError(ContractDiffError):
    """文件格式错误"""
    def __init__(self, message, expected_format=None):
        error_code = "FILE_FORMAT_ERROR"
        if expected_format:
            message = f"文件格式错误（期望：{expected_format}）\n{message}"
        super().__init__(message, error_code)


class CompareError(ContractDiffError):
    """对比过程错误"""
    def __init__(self, message, step=None):
        error_code = "COMPARE_ERROR"
        if step:
            message = f"对比失败（步骤：{step}）\n{message}"
        super().__init__(message, error_code)


class OutputError(ContractDiffError):
    """输出文件错误"""
    def __init__(self, message, output_path=None):
        error_code = "OUTPUT_ERROR"
        if output_path:
            message = f"无法生成输出文件：{output_path}\n{message}"
        super().__init__(message, error_code)


class NetworkError(ContractDiffError):
    """网络错误（用于自动更新）"""
    def __init__(self, message, url=None):
        error_code = "NETWORK_ERROR"
        if url:
            message = f"网络请求失败：{url}\n{message}"
        super().__init__(message, error_code)


class UpdateError(ContractDiffError):
    """更新错误"""
    def __init__(self, message):
        super().__init__(message, "UPDATE_ERROR")


def get_friendly_error_message(exception):
    """获取友好的错误提示信息"""
    error_messages = {
        FileLoadError: "无法加载文件，请检查文件是否存在且未被其他程序占用。",
        FileFormatError: "文件格式不支持，请确保使用 .docx 或 .pdf 格式的文件。",
        CompareError: "对比过程中发生错误，请重试或查看日志获取详细信息。",
        OutputError: "无法保存结果文件，请检查保存路径是否有写入权限。",
        NetworkError: "网络连接失败，请检查网络连接后重试。",
        UpdateError: "检查更新失败，请稍后重试。",
    }
    
    error_type = type(exception)
    if error_type in error_messages:
        return error_messages[error_type]
    
    # 通用错误消息
    return f"发生错误：{str(exception)}\n\n如问题持续，请查看日志文件或联系技术支持。"
