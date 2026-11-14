$ErrorActionPreference = 'Stop'
$geRepo = 'C:/Users/gk/.codex/worktrees/nba-vae-longrun-40/Cybernetic_City_State_OS_v2 - nba2k22'
Set-Location -LiteralPath $geRepo
& 'C:/Users/gk/AppData/Local/Python/pythoncore-3.14-64/python.exe' -B -X utf8 (Join-Path $geRepo '01_os/07_content/_runs/run-20261111-nba2k22-live-research-continuation-001/evidence/ge01_entry.py') 1> 'C:/Users/gk/Documents/ChatGPT/nba2k22/ge01-runtime/entry.stdout.log' 2> 'C:/Users/gk/Documents/ChatGPT/nba2k22/ge01-runtime/entry.stderr.log'
$geExit = $LASTEXITCODE
Set-Content -LiteralPath 'C:/Users/gk/Documents/ChatGPT/nba2k22/ge01-runtime/entry.exit.txt' -Value $geExit
exit $geExit
