param([Parameter(Mandatory=$true)][string]$RepoRoot)
$ErrorActionPreference = 'Stop'
$prmsTokens = $null
$prmsErrors = $null
$prmsTarget = Join-Path (Resolve-Path -LiteralPath $RepoRoot).Path 'new-domain.ps1'
$null = [System.Management.Automation.Language.Parser]::ParseFile($prmsTarget, [ref]$prmsTokens, [ref]$prmsErrors)
if ($prmsErrors.Count -gt 0) {
    throw ($prmsErrors | ForEach-Object Message | Out-String)
}
@{status='SYNTAX_VALID'; target='new-domain.ps1'; script_executed=$false; real_domain_created=$false} | ConvertTo-Json -Compress
