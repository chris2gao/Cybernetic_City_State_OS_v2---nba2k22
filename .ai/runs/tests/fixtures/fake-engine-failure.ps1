param([Parameter(Mandatory = $true)][string]$Worktree)
Write-Error 'synthetic worker failure'
Start-Sleep -Seconds 1
exit 7
