#!/bin/bash
# Linux 定时清理脚本
# 每周运行一次，清理旧数据

# 切换到脚本目录
cd "$(dirname "$0")"

# 生成日志文件名（带日期）
LOGFILE="cleanup_$(date +%Y%m%d).log"

echo "==========================================" >> "$LOGFILE"
echo "开始清理任务 - $(date)" >> "$LOGFILE"
echo "==========================================" >> "$LOGFILE"

# 执行清理
python cleanup_old_data.py --cleanup-logs 30 --cleanup-keywords >> "$LOGFILE" 2>&1

echo "==========================================" >> "$LOGFILE"
echo "清理任务完成 - $(date)" >> "$LOGFILE"
echo "==========================================" >> "$LOGFILE"
echo "" >> "$LOGFILE"

# 保留最近30天的日志，删除旧日志
find . -name "cleanup_*.log" -mtime +30 -delete 2>/dev/null

echo "清理完成！日志已保存到 $LOGFILE"
