@echo off
REM Windows 服务启动脚本

echo ========================================
echo DHT 搜索引擎 - 服务启动
echo ========================================
echo.

REM 检查 PM2 是否安装
where pm2 >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [错误] PM2 未安装
    echo 请运行: npm install -g pm2
    pause
    exit /b 1
)

REM 切换到项目目录
cd /d %~dp0

REM 创建日志目录
if not exist "logs" mkdir logs

echo [1/4] 停止旧服务...
pm2 delete all >nul 2>nul

echo [2/4] 启动所有服务...
pm2 start ecosystem.config.js

echo [3/4] 查看服务状态...
pm2 status

echo [4/4] 保存进程列表...
pm2 save

echo.
echo ========================================
echo ✅ 所有服务已启动
echo ========================================
echo.
echo 常用命令:
echo   查看状态: pm2 status
echo   查看日志: pm2 logs
echo   重启服务: pm2 restart all
echo   停止服务: pm2 stop all
echo.
pause
