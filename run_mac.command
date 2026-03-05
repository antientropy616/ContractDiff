#!/bin/bash
# 合同对比助手 - macOS 启动脚本（源码运行版）
# 无需打包，直接运行源码

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_PYTHON="$SCRIPT_DIR/venv/bin/python3"

echo "🚀 正在启动合同对比助手..."
echo "📁 工作目录：$SCRIPT_DIR"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ 错误：找不到虚拟环境 Python"
    echo "请先运行：python3 -m venv venv"
    exit 1
fi

echo "✅ Python: $($VENV_PYTHON --version)"
echo "✅ 虚拟环境：$VENV_PYTHON"
echo ""

cd "$SCRIPT_DIR"
exec "$VENV_PYTHON" src/main.py
