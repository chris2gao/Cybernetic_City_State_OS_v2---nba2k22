[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$Career,
      [string]$QueryRoot = (Join-Path $PSScriptRoot '..\database\query_snapshots'))
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $repoRoot
try {
    python -B -m unittest discover -s tests -p test_gm_data_access.py -v
    if ($LASTEXITCODE -ne 0) { throw 'M0 synthetic tests failed' }
    python -B scripts/check_gm_sqlite_m0.py --career $Career --query-root $QueryRoot
    if ($LASTEXITCODE -ne 0) { throw 'M0 local CLI verification failed' }
} finally { Pop-Location }
