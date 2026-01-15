#!/bin/bash
# Linux 服务启动脚本

echo "========================================"
echo "DHT 搜索引擎 - 服务启动"
echo "========================================"
echo ""

# 检查依赖环境
if ! command -v pm2 &> /dev/null; then
    echo "[错误] PM2 未安装 (npm install -g pm2)"
    exit 1
fi

if ! command -v pipenv &> /dev/null; then
    echo "[错误] Pipenv 未安装 (pip install pipenv)"
    exit 1
fi

# 切换到脚本目录
cd "$(dirname "$0")"

# 创建日志目录
mkdir -p logs

echo "[1/4] 停止旧服务..."
pm2 delete all > /dev/null 2>&1

echo "[2/4] 启动所有服务..."
pm2 start ecosystem.config.js

echo "[3/4] 查看服务状态..."
pm2 status

echo "[4/4] 保存进程列表..."
pm2 save

echo ""
echo "========================================"
echo "✅ 所有服务已启动"
echo "========================================"
echo ""
echo "常用命令:"
echo "  查看状态: pm2 status"
echo "  查看日志: pm2 logs"
echo "  重启服务: pm2 restart all"
echo "  停止服务: pm2 stop all"
echo ""
