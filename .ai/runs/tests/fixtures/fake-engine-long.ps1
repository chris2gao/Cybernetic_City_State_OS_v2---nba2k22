param([Parameter(Mandatory = $true)][string]$Worktree)
$child = Start-Process -FilePath powershell.exe -ArgumentList '-NoProfile -NonInteractive -Command "Start-Sleep -Seconds 120"' -PassThru -WindowStyle Hidden
[IO.File]::WriteAllText((Join-Path $Worktree 'child.pid'), [string]$child.Id)
Write-Output '{"type":"thread.started","thread_id":"019f-test-session-long"}'
Start-Sleep -Seconds 120
exit 0
