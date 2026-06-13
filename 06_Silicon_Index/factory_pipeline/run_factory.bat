@echo off
echo ========================================================
echo   Cybernetic City State OS v9.1 - The Great Synthesis
echo   Autonomous Factory Engine
echo ========================================================
echo.

:: 检查是否配置了 API KEY
if "%OPENAI_API_KEY%"=="" (
    echo [WARNING] 环境变量 OPENAI_API_KEY 未设置！
    echo 请先设置 API 密钥。例如在终端中运行：
    echo set OPENAI_API_KEY=sk-xxxxx
    echo.
    echo 你也可以设置其他兼容大模型的 Base URL：
    echo set OPENAI_BASE_URL=https://api.deepseek.com/v1
    echo.
    pause
    exit /b 1
)

echo [INFO] 检测到 API Key。正在启动全自动流水线...
echo.

cd /d "%~dp0"
python autonomous_factory_agent.py

echo.
echo [INFO] 执行完毕或因错误退出。状态已保存在 generation_state.json。
pause
