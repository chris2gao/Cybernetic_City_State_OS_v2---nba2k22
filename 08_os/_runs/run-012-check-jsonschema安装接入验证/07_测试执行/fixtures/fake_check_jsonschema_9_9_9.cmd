@echo off
if "%~1"=="--version" (
  echo check-jsonschema, version 9.9.9
  exit /b 0
)
if not "%CJV_SENTINEL%"=="" echo validation-ran>"%CJV_SENTINEL%"
exit /b 0
