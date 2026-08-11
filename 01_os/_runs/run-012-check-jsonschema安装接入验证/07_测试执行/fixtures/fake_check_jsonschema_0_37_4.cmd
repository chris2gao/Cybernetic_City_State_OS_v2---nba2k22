@echo off
if "%~1"=="--version" (
  echo check-jsonschema, version 0.37.4
  exit /b 0
)
if not "%CJV_SENTINEL%"=="" echo validation-ran>"%CJV_SENTINEL%"
exit /b 0
