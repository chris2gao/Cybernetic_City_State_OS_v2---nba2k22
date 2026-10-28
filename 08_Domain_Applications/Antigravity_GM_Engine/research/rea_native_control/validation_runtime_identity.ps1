$ErrorActionPreference = 'Stop'
$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Approved validation must be explicitly launched in an administrator session'
}
$games = @(Get-Process NBA2K22 -ErrorAction Stop)
if ($games.Count -ne 1) { throw 'Exactly one NBA2K22 game process is required' }
$game = $games[0]
[ordered]@{
    pid = $game.Id
    process_start_utc = $game.StartTime.ToUniversalTime().ToString('o')
    exe_sha256 = (Get-FileHash -LiteralPath $game.MainModule.FileName -Algorithm SHA256).Hash.ToLowerInvariant()
} | ConvertTo-Json
