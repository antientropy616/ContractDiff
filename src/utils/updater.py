#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动更新模块
检查新版本并提示用户更新
"""

import json
import os
import re
from datetime import datetime
from utils.logger import logger
from utils.error_handler import NetworkError, UpdateError

# 更新检查配置
UPDATE_CONFIG = {
    'version_file': 'https://raw.githubusercontent.com/your-repo/contract-diff/main/version.json',
    'current_version': '1.2',
    'check_interval_days': 7,
    'last_check_file': 'last_update_check.json'
}


class AutoUpdater:
    """自动更新管理器"""
    
    def __init__(self):
        self.current_version = UPDATE_CONFIG['current_version']
        self.config_dir = os.path.join(
            os.path.expanduser("~"),
            "Documents",
            "合同对比助手"
        )
        os.makedirs(self.config_dir, exist_ok=True)
        
        self.last_check_file = os.path.join(
            self.config_dir,
            UPDATE_CONFIG['last_check_file']
        )
    
    def should_check_update(self):
        """检查是否应该进行更新检查"""
        if not os.path.exists(self.last_check_file):
            return True
        
        try:
            with open(self.last_check_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                last_check = datetime.fromisoformat(data.get('last_check', ''))
                days_since_check = (datetime.now() - last_check).days
                return days_since_check >= UPDATE_CONFIG['check_interval_days']
        except Exception as e:
            logger.warning(f"读取更新检查记录失败：{e}")
            return True
    
    def check_for_updates(self):
        """检查新版本"""
        logger.info("开始检查更新...")
        
        # 模拟版本检查（实际部署时替换为真实网络请求）
        # 这里使用本地模拟，避免实际网络依赖
        try:
            # 实际部署时使用：
            # import requests
            # response = requests.get(UPDATE_CONFIG['version_file'], timeout=10)
            # response.raise_for_status()
            # remote_data = response.json()
            
            # 模拟响应（开发阶段）
            remote_data = {
                'version': '1.2',  # 当前最新版本
                'release_date': '2026-03-03',
                'changes': [
                    '添加日志系统 - 方便排查问题',
                    '添加异常捕获 - 更友好的错误提示',
                    '添加单元测试 - 保证代码质量',
                    '添加自动更新 - 方便版本升级',
                    '添加 PDF 支持 - 扩展使用场景',
                    '新增【更新说明】菜单项'
                ],
                'download_url': 'https://github.com/your-repo/contract-diff/releases/latest'
            }
            
            latest_version = remote_data.get('version', '0.0')
            
            # 保存检查时间
            self._save_check_time()
            
            # 比较版本号
            if self._compare_versions(latest_version, self.current_version) > 0:
                logger.info(f"发现新版本：{latest_version}（当前：{self.current_version}）")
                return {
                    'has_update': True,
                    'version': latest_version,
                    'release_date': remote_data.get('release_date', ''),
                    'changes': remote_data.get('changes', []),
                    'download_url': remote_data.get('download_url', '')
                }
            else:
                logger.info("已是最新版本")
                return {'has_update': False}
                
        except Exception as e:
            logger.error(f"检查更新失败：{e}", exc_info=True)
            raise NetworkError(f"检查更新失败：{str(e)}")
    
    def _save_check_time(self):
        """保存检查时间"""
        try:
            data = {
                'last_check': datetime.now().isoformat(),
                'version_checked': self.current_version
            }
            with open(self.last_check_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"保存检查时间失败：{e}")
    
    def _compare_versions(self, v1, v2):
        """比较版本号，返回 1（v1>v2）、0（v1=v2）、-1（v1<v2）"""
        def normalize(v):
            return [int(x) for x in re.sub(r'[^0-9.]', '', v).split('.')]
        
        parts1 = normalize(v1)
        parts2 = normalize(v2)
        
        # 补齐长度
        max_len = max(len(parts1), len(parts2))
        parts1.extend([0] * (max_len - len(parts1)))
        parts2.extend([0] * (max_len - len(parts2)))
        
        for p1, p2 in zip(parts1, parts2):
            if p1 > p2:
                return 1
            elif p1 < p2:
                return -1
        return 0
    
    def get_changelog(self):
        """获取更新日志"""
        changelog_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'CHANGELOG.md'
        )
        
        if os.path.exists(changelog_path):
            try:
                with open(changelog_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"读取更新日志失败：{e}")
        
        # 默认更新日志
        return self._get_default_changelog()
    
    def _get_default_changelog(self):
        """获取默认更新日志"""
        return """# 合同对比助手 - 版本更新日志

## v1.2 (2026-03-03)

### 🛠️ 新增功能

1. **日志系统**
   - 自动记录运行日志
   - 日志文件按天轮转
   - 日志位置：`~/Documents/合同对比助手/logs/`

2. **异常捕获**
   - 友好的错误提示
   - 详细的错误日志
   - 分类异常处理

3. **单元测试**
   - 核心功能测试覆盖
   - 自动化测试框架
   - 保证代码质量

4. **自动更新**
   - 定期检查新版本
   - 更新提示
   - 一键跳转下载

5. **PDF 支持**
   - 支持 PDF 文档对比
   - PDF 转 Word 处理
   - 扩展使用场景

6. **更新说明**
   - 帮助菜单新增【更新说明】
   - 查看历史版本变更

---

## v1.1 (2026-03-03)

### 🛠️ 改进与优化

1. **简化输出选项**
   - 移除了未实际生效的"侧边批注"和"颜色高亮"选项
   - 输出选项更加清晰，避免用户困惑

2. **命名优化**
   - "Word 修订模式"更名为"详细改动列表"
   - 名称更准确反映实际功能

3. **功能精简**
   - 移除了日期变化识别功能
   - 减少误报，提升对比准确性

---

## v1.0 (2026-02-28)

### 🎉 首次发布

- 自动识别文字增删改
- 支持 Word 修订模式输出
- 生成独立对比报告
- 专业法律风格界面
"""

# 全局更新器实例
updater = AutoUpdater()
