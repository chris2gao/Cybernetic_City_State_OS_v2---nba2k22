# Reviewer probe: does the FROZEN ACCEPTANCE PACKAGE catch the defects the
# canonical validator lets through?  Runs the real harness (from its real
# location) against mutated copies of the whole working tree.
$ErrorActionPreference = 'Continue'
$repo = 'E:\newStand\study\Cybernetic_City_State_OS_v2 - core'
$base = 'C:\s07\trees'
$RUN  = "$repo\01_os\_runs\run-20260811-全局模型能力与可用性机制-001"
$VS   = "$RUN\04_测试生成\实现\verify_stage04_acceptance.py"
$CAT  = '01_os\03_mechanisms\model_routing\模型与产品面目录_v1.yml'
$SRC  = '01_os\03_mechanisms\model_routing\来源索引_v1.yml'
$REG  = '01_os\05_registry\model_routing_v1.yml'

function New-Tree($name) {
  $dst = Join-Path $base $name
  if (Test-Path $dst) { Remove-Item $dst -Recurse -Force }
  New-Item -ItemType Directory -Force -Path $dst | Out-Null
  robocopy $repo $dst /E /NFL /NDL /NJH /NJS /NP /XD '.git' '08_os' '__pycache__' '.pytest_cache' | Out-Null
  return $dst
}

function Run-Acceptance($tree, $label) {
  $log = "C:\s07\acc_$label.log"
  python $VS acceptance $tree *> $log
  $code = $LASTEXITCODE
  $fails = @(Select-String -Path $log -Pattern '^FAIL ' | ForEach-Object { ($_.Line -split '\s+')[1] })
  "{0,-6} exit={1} failing_tests={2}" -f $label, $code, ($(if ($fails.Count) { $fails -join ',' } else { 'NONE' }))
}

# X01 - source locator degraded to a nonexistent in-repo path
$t = New-Tree 'X01'
$p = Join-Path $t $SRC
$txt = Get-Content $p -Raw
$txt = $txt -replace '(?m)^(  GOOGLE_AG_MODELS:\r?\n    kind: provider_first_party\r?\n    title: Google Antigravity Models\r?\n)    url: https://antigravity\.google/docs/models', '$1    path: 01_os/03_mechanisms/model_routing/绝不存在_v9.yml'
Set-Content -Path $p -Value $txt -Encoding utf8 -NoNewline
"X01 anchor_applied=" + ($txt -match '绝不存在_v9')
Run-Acceptance $t 'X01'

# X02 - economic routing field smuggled into a catalog entry
$t = New-Tree 'X02'
$p = Join-Path $t $CAT
$txt = Get-Content $p -Raw
$txt = $txt -replace '(?m)^(    model_label: GPT-5\.6 Sol\r?\n)', "`$1    price_weight: 0.4`r`n"
Set-Content -Path $p -Value $txt -Encoding utf8 -NoNewline
"X02 anchor_applied=" + ($txt -match 'price_weight')
Run-Acceptance $t 'X02'

# X03 - registry collapsed into one over-broad 01_os/** wildcard
$t = New-Tree 'X03'
$p = Join-Path $t $REG
$txt = Get-Content $p -Raw
$txt = $txt -replace '(?m)^  - path: 01_os/03_mechanisms/model_routing/\*\*', '  - path: 01_os/**'
Set-Content -Path $p -Value $txt -Encoding utf8 -NoNewline
"X03 anchor_applied=" + ($txt -match '(?m)^  - path: 01_os/\*\*')
Run-Acceptance $t 'X03'

# X06 - Opus 4.8 moved back onto antigravity (the original F1 shape)
$t = New-Tree 'X06'
$p = Join-Path $t $CAT
$txt = Get-Content $p -Raw
$txt = $txt -replace '(?m)^(    surface_id: )claude_code_desktop(\r?\n    model_label: Claude Opus 4\.8)', '$1antigravity$2'
Set-Content -Path $p -Value $txt -Encoding utf8 -NoNewline
"X06 anchor_applied=" + ($txt -match '(?m)^    surface_id: antigravity\r?\n    model_label: Claude Opus 4\.8')
Run-Acceptance $t 'X06'

# control - unmutated full-tree copy must be 35/35 green
$t = New-Tree 'CTRL'
Run-Acceptance $t 'CTRL'
