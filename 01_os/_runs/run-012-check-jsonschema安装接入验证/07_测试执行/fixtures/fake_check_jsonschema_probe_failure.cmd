@echo off
if "%~1"=="--version" (
  echo probe failed 1>&2
  exit /b 7
)
if not "%CJV_SENTINEL%"=="" echo validation-ran>"%CJV_SENTINEL%"
exit /b 0
