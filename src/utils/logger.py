#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志系统模块
提供统一的日志管理功能
"""

import os
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler


class Logger:
    """统一日志管理器"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if Logger._initialized:
            return
        
        Logger._initialized = True
        self.logger = logging.getLogger('ContractDiff')
        self.logger.setLevel(logging.DEBUG)
        
        # 创建日志目录
        log_dir = os.path.join(os.path.expanduser("~"), "Documents", "合同对比助手", "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # 日志文件路径
        log_file = os.path.join(log_dir, f"contrast_{datetime.now().strftime('%Y%m%d')}.log")
        
        # 文件处理器（轮转，最大 5MB，保留 3 个文件）
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5*1024*1024,
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, message):
        """调试日志"""
        self.logger.debug(message)
    
    def info(self, message):
        """信息日志"""
        self.logger.info(message)
    
    def warning(self, message):
        """警告日志"""
        self.logger.warning(message)
    
    def error(self, message, exc_info=False):
        """错误日志"""
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message, exc_info=False):
        """严重错误日志"""
        self.logger.critical(message, exc_info=exc_info)
    
    def get_log_file_path(self):
        """获取当前日志文件路径"""
        log_dir = os.path.join(os.path.expanduser("~"), "Documents", "合同对比助手", "logs")
        return os.path.join(log_dir, f"contrast_{datetime.now().strftime('%Y%m%d')}.log")


# 全局日志实例
logger = Logger()
