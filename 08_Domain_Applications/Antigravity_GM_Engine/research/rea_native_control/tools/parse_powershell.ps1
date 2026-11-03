param([Parameter(Mandatory=$true)][string]$Path)
$tokens=$null;$parseErrors=$null
[System.Management.Automation.Language.Parser]::ParseFile($Path,[ref]$tokens,[ref]$parseErrors) | Out-Null
if($parseErrors.Count){$parseErrors | ForEach-Object {$_.Message};exit 1}
