#!/bin/bash

# 豆瓣爬虫快速启动脚本

echo "=================================="
echo "   豆瓣书籍爬虫 - 快速启动"
echo "=================================="
echo ""

# 检查是否安装了uv
if ! command -v uv &> /dev/null; then
    echo "❌ 错误: 未安装uv"
    echo "请先安装uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "📦 首次运行，正在安装依赖..."
    uv sync
fi

echo "🚀 启动爬虫..."
echo ""

# 运行爬虫
uv run python douban_spider_v2.py

echo ""
echo "✓ 爬取完成！"
