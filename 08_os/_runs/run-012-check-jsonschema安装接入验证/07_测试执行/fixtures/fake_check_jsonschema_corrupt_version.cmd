@echo off
if "%~1"=="--version" (
  echo version unknown
  exit /b 0
)
if not "%CJV_SENTINEL%"=="" echo validation-ran>"%CJV_SENTINEL%"
exit /b 0
