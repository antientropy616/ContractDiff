# 合同对比助手 - macOS 版更新日志

## v1.2.3-Mac (2026-03-05)

### 🎉 macOS 原生支持

**新增功能：**
- ✅ 新增 macOS 构建脚本 `build_mac.py`
- ✅ 新增 macOS PyInstaller 配置 `contract_diff_mac.spec`
- ✅ 生成原生 `.app` 应用程序包
- ✅ 自动创建启动脚本 `启动合同对比助手.command`
- ✅ 自动生成使用说明文档

**跨平台优化：**
- ✅ 字体自动选择（Windows: 微软雅黑，macOS: 苹方，Linux: 文泉驿）
- ✅ 路径显示格式自动适配（Windows: `\`，macOS/Linux: `/`）
- ✅ 日志文件路径跨平台兼容
- ✅ 所有核心模块支持 macOS

**文件变更：**
- `src/main.py` - 添加跨平台字体支持
- `src/ui/main_window.py` - 添加 `get_system_font()` 函数，路径显示适配
- `src/utils/logger.py` - 日志路径跨平台优化
- `README.md` - 添加 macOS 构建说明
- `version.json` - 更新版本信息

**新增文件：**
- `build_mac.py` - macOS 构建脚本
- `contract_diff_mac.spec` - macOS PyInstaller 配置
- `macOS 移植说明.md` - 详细移植文档
- `CHANGELOG_MAC.md` - 本文件

---

## v1.2.3 (2026-03-04) - Windows

### 🐛 Bug 修复
- 修复：doc_comparator 类定义缩进错误导致无法启动
- 修复：页眉页脚提取 AttributeError（'_Header' object has no attribute 'text'）

### ⚡ 优化
- 优化：详细改动列表中位置显示改为「第 X 段」更直观
- 优化：关于对话框增加「玉哥与他的虾」署名
- 优化：版本号从 version.json 动态读取
- 清理：删除开发阶段临时测试文件和无用文档

---

## v1.2 (2026-03-03)

### 🛠️ 新增功能
1. **日志系统** - 自动记录运行日志
2. **异常捕获** - 友好的错误提示
3. **单元测试** - 核心功能测试覆盖
4. **自动更新** - 定期检查新版本
5. **PDF 支持** - 支持 PDF 文档对比
6. **更新说明** - 帮助菜单新增【更新说明】

---

## v1.0 (2026-02-28)

### 🎉 首次发布
- 自动识别文字增删改
- 支持 Word 修订模式输出
- 生成独立对比报告
- 专业法律风格界面

---

*最后更新：2026-03-05*
