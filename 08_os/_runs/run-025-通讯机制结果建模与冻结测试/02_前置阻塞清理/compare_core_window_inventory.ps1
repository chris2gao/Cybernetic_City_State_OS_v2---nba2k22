param(
    [Parameter(Mandatory = $true)][string]$First,
    [Parameter(Mandatory = $true)][string]$Second,
    [Parameter(Mandatory = $true)][string]$Output
)

$ErrorActionPreference = "Stop"
$firstHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $First).Hash.ToLowerInvariant()
$secondHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $Second).Hash.ToLowerInvariant()
$firstData = Get-Content -LiteralPath $First -Raw | ConvertFrom-Json
$secondData = Get-Content -LiteralPath $Second -Raw | ConvertFrom-Json
$consistent = $firstHash -eq $secondHash
$result = [ordered]@{
    artifact_type = "core_window_inventory_consistency"
    method_version = 1
    byte_identical = $consistent
    first_sha256 = $firstHash
    second_sha256 = $secondHash
    base_commit_equal = $firstData.base_commit -eq $secondData.base_commit
    coverage_boundary_equal = ($firstData.coverage | ConvertTo-Json -Depth 8 -Compress) -eq ($secondData.coverage | ConvertTo-Json -Depth 8 -Compress)
    not_observable_preserved = @($firstData.coverage.not_observable).Count -gt 0
}
if (Test-Path -LiteralPath $Output) {
    throw "Immutable output already exists: $([System.IO.Path]::GetFileName($Output))"
}
$parent = Split-Path -Parent $Output
New-Item -ItemType Directory -Path $parent -Force | Out-Null
$temp = Join-Path $parent (".$([System.IO.Path]::GetFileName($Output)).$([Guid]::NewGuid().ToString('N')).tmp")
try {
    [System.IO.File]::WriteAllText($temp, ($result | ConvertTo-Json -Depth 5) + "`n", [System.Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $temp -Destination $Output
}
finally {
    if (Test-Path -LiteralPath $temp) {
        Remove-Item -LiteralPath $temp
    }
}
Write-Output ($result | ConvertTo-Json -Compress)
if (-not $consistent) {
    exit 1
}
