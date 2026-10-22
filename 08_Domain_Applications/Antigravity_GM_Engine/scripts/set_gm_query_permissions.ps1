<# Owner-only preparation for a DIFFERENT non-admin consumer account.
   Changes ACLs only; no game process, database content writes or publication.
   Do not run in the consumer Web terminal. See docs/GM_SQLITE_QUERY_ACCESS.md.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$ConsumerAccount,
    [Parameter(Mandatory=$true)][string]$QueryRoot,
    [Parameter(Mandatory=$true)][string]$AuthoritySavesRoot
)
$ErrorActionPreference = 'Stop'
$queryPath = (Resolve-Path -LiteralPath $QueryRoot).Path
$authorityPath = (Resolve-Path -LiteralPath $AuthoritySavesRoot).Path
if ($queryPath -eq $authorityPath -or $queryPath.StartsWith($authorityPath + '\') -or $authorityPath.StartsWith($queryPath + '\')) {
    throw 'Query snapshots and authority saves must be disjoint directories'
}
if ((Get-Item -LiteralPath $queryPath).Name -ne 'query_snapshots' -or (Get-Item -LiteralPath $authorityPath).Name -ne 'saves') {
    throw 'Expected explicit query_snapshots and saves directories'
}
$owner = [System.Security.Principal.WindowsIdentity]::GetCurrent().User
$consumer = ([System.Security.Principal.NTAccount]::new($ConsumerAccount)).Translate([System.Security.Principal.SecurityIdentifier])
if ($consumer -eq $owner -or $consumer.Value -in @('S-1-5-18','S-1-5-32-544','S-1-1-0','S-1-5-11','S-1-5-32-545')) {
    throw 'Use a distinct dedicated account, not the owner or a shared group'
}
# Consumer must have no delete-child rights on the parent of the query root.
# Deny mutation there, including inherited broad Users/Authenticated Users grants.
$parentPath = Split-Path -Parent $queryPath
$parentAcl = Get-Acl -LiteralPath $parentPath
$denyParent = [System.Security.AccessControl.FileSystemAccessRule]::new($consumer, 'Write,Delete,DeleteSubdirectoriesAndFiles', 'None', 'None', 'Deny')
$parentAcl.AddAccessRule($denyParent)
Set-Acl -LiteralPath $parentPath -AclObject $parentAcl
$items = @((Get-Item -LiteralPath $queryPath)) + @(Get-ChildItem -LiteralPath $queryPath -Force -Recurse)
foreach ($item in $items) {
    if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) { throw 'Reparse points are not permitted' }
    $acl = Get-Acl -LiteralPath $item.FullName
    $acl.SetAccessRuleProtection($true, $false)
    foreach ($entry in @($acl.Access)) { $acl.RemoveAccessRuleSpecific($entry) }
    $inherit = if ($item.PSIsContainer) { 'ContainerInherit,ObjectInherit' } else { 'None' }
    foreach ($sid in @($owner, [System.Security.Principal.SecurityIdentifier]::new('S-1-5-18'), [System.Security.Principal.SecurityIdentifier]::new('S-1-5-32-544'))) {
        $acl.AddAccessRule([System.Security.AccessControl.FileSystemAccessRule]::new($sid, 'FullControl', $inherit, 'None', 'Allow'))
    }
    $acl.AddAccessRule([System.Security.AccessControl.FileSystemAccessRule]::new($consumer, 'ReadAndExecute', $inherit, 'None', 'Allow'))
    $acl.AddAccessRule([System.Security.AccessControl.FileSystemAccessRule]::new($consumer, 'Write,Delete,DeleteSubdirectoriesAndFiles', $inherit, 'None', 'Deny'))
    Set-Acl -LiteralPath $item.FullName -AclObject $acl
}
$authorityAcl = Get-Acl -LiteralPath $authorityPath
$authorityAcl.AddAccessRule([System.Security.AccessControl.FileSystemAccessRule]::new($consumer, 'FullControl', 'ContainerInherit,ObjectInherit', 'None', 'Deny'))
Set-Acl -LiteralPath $authorityPath -AclObject $authorityAcl
Write-Output 'CONSUMER_READ_ONLY_ACL_CONFIGURED; verify from the separate non-admin account when connected'
