param([Parameter(Mandatory = $true)][string]$Worktree)
$child = Start-Process -FilePath powershell.exe -ArgumentList '-NoProfile -NonInteractive -Command "Start-Sleep -Seconds 120"' -PassThru -WindowStyle Hidden
[IO.File]::WriteAllText((Join-Path $Worktree 'child.pid'), [string]$child.Id)
Write-Output 'api_key=synthetic-test-value-that-must-not-persist'
Start-Sleep -Seconds 2
Write-Output '{"type":"thread.started","thread_id":"019f-test-session-0001"}'
exit 0
