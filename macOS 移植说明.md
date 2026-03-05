# 合同对比助手 - macOS 移植说明

## 版本信息
- **移植日期**: 2026-03-05
- **基础版本**: v1.2.3 (Windows)
- **macOS 版本**: v1.2.3-Mac

---

## 主要改动

### 1. 跨平台字体支持
**文件**: `src/main.py`, `src/ui/main_window.py`

- Windows: Microsoft YaHei (微软雅黑)
- macOS: PingFang SC (苹方)
- Linux: WenQuanYi Micro Hei (文泉驿微米黑)

```python
def get_system_font():
    """获取系统字体（跨平台兼容）"""
    system = platform.system()
    if system == "Darwin":  # macOS
        return "PingFang SC"
    elif system == "Windows":
        return "Microsoft YaHei"
    else:  # Linux 等其他系统
        return "WenQuanYi Micro Hei"
```

### 2. 路径显示格式
**文件**: `src/ui/main_window.py`

- Windows: `C:\Users\...\Documents\合同对比结果_时间戳.docx`
- macOS: `~/Documents/合同对比结果_时间戳.docx`

### 3. macOS 构建脚本
**新增文件**: `build_mac.py`

生成 `.app` 应用程序包，包含：
- 自动复制到 `~/Documents/` 文件夹
- 创建启动脚本 `启动合同对比助手.command`
- 生成使用说明文档

### 4. PyInstaller 配置
**新增文件**: `contract_diff_mac.spec`

针对 macOS 优化的打包配置。

---

## 构建流程

### 在 macOS 上构建

```bash
# 1. 进入项目目录
cd /path/to/合同对比助手

# 2. 安装依赖（如果还没有）
pip3 install -r requirements.txt

# 3. 执行构建
python3 build_mac.py

# 4. 构建完成
# App 位于：~/Documents/合同对比助手.app
```

### 构建调试版

```bash
python3 build_mac.py --debug
```

---

## 已知问题与注意事项

### 1. 首次运行安全提示
macOS 会提示"无法打开，因为来自身份不明的开发者"

**解决方法**:
1. 打开"系统偏好设置" → "安全性与隐私"
2. 在"通用"标签页找到提示
3. 点击"仍要打开"

### 2. PDF 支持
PDF 功能需要额外安装依赖：
```bash
pip3 install pdfplumber pdf2docx
```

### 3. 日志文件位置
```
~/Documents/合同对比助手/logs/
```

### 4. 配置文件位置
```
~/Documents/合同对比助手/
- last_update_check.json (更新检查记录)
- logs/ (日志文件夹)
```

---

## 测试清单

构建后请测试以下功能：

- [ ] 程序正常启动
- [ ] 选择 Word 文档 (.docx)
- [ ] 执行文档对比
- [ ] 生成结果文档
- [ ] 导出 Excel 报告
- [ ] 查看关于对话框
- [ ] 检查更新功能
- [ ] 日志文件正常生成
- [ ] 界面字体显示正常
- [ ] 路径显示格式正确

---

## 后续优化建议

1. **代码签名**: 为 App 添加开发者签名，避免安全提示
2. **DMG 打包**: 创建 .dmg 安装包，方便分发
3. **Sparkle 更新**: 集成 macOS 原生更新框架
4. **菜单栏图标**: 添加系统菜单栏快捷入口
5. **快捷键支持**: 优化 macOS 快捷键习惯（Cmd 替代 Ctrl）

---

## 开发者联系

玉哥与他的虾
2026-03-05
