@echo off
REM Windows 定时清理脚本
REM 每周运行一次，清理旧数据

cd /d %~dp0

REM 生成日志文件名（带日期）
set LOGFILE=cleanup_%date:~0,4%%date:~5,2%%date:~8,2%.log

echo ========================================== >> %LOGFILE%
echo 开始清理任务 - %date% %time% >> %LOGFILE%
echo ========================================== >> %LOGFILE%

REM 执行清理
python cleanup_old_data.py --cleanup-logs 30 --cleanup-keywords >> %LOGFILE% 2>&1

echo ========================================== >> %LOGFILE%
echo 清理任务完成 - %date% %time% >> %LOGFILE%
echo ========================================== >> %LOGFILE%
echo. >> %LOGFILE%

REM 保留最近30天的日志，删除旧日志
forfiles /p "%~dp0" /m cleanup_*.log /d -30 /c "cmd /c del @path" 2>nul

echo 清理完成！日志已保存到 %LOGFILE%
