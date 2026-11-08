# Run Epic BuildGraph on a trusted persistent Windows machine.
# Licensed source, graph JSON, binaries and raw logs stay private.
[CmdletBinding()]
param(
  [Parameter(Mandatory)][ValidateSet('export','node','resume')][string]$Mode,
  [Parameter(Mandatory)][string]$EngineRoot,
  [Parameter(Mandatory)][string]$SharedRoot,
  [string]$NodeName = ''
)
$ErrorActionPreference='Stop'
$EngineRoot=[IO.Path]::GetFullPath($EngineRoot)
$SharedRoot=[IO.Path]::GetFullPath($SharedRoot)
$script=Join-Path $EngineRoot 'Engine/Build/InstalledEngineBuild.xml'
$uat=Join-Path $EngineRoot 'Engine/Build/BatchFiles/RunUAT.bat'
if (!(Test-Path -LiteralPath $uat -PathType Leaf) -or !(Test-Path -LiteralPath $script -PathType Leaf)) { throw 'Licensed Unreal 5.8 checkout missing on self-hosted machine.' }
if (!(Test-Path -LiteralPath $SharedRoot -PathType Container)) { throw 'Private persistent shared-storage directory is required.' }
if ($env:GITHUB_WORKSPACE) {
  $repoRoot=[IO.Path]::GetFullPath($env:GITHUB_WORKSPACE).TrimEnd('\') + '\'
  if ($SharedRoot.StartsWith($repoRoot,[StringComparison]::OrdinalIgnoreCase)) { throw 'Private outputs must be outside public repository checkout.' }
}
if ($Mode -eq 'node' -and $NodeName -notmatch '^[\w .()+-]{1,160}$') { throw 'Invalid or empty BuildGraph node name.' }
$settings=@(
  'WithWin64=true','WithWin32=false','WithAndroid=true','WithDDC=false',
  'WithLinux=false','WithLinuxArm64=false','WithMac=false','WithIOS=false',
  'WithTVOS=false','WithFullDebugInfo=false','WithClient=false','WithServer=false',
  'GameConfigurations=Development'
)
$revision=(& git -C $EngineRoot rev-parse HEAD 2>$null) -join ''
if ($LASTEXITCODE -ne 0 -or !$revision) { throw 'Require a Git-backed licensed source checkout to safely fingerprint build products.' }
$signatureInput=$revision + '|' + (Get-FileHash -LiteralPath $script -Algorithm SHA256).Hash + '|' + ($settings -join '|')
$signature=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($signatureInput)))
$manifest=Join-Path $SharedRoot 'manifest.json'
$graph=Join-Path $SharedRoot 'installed-engine-graph.json'
$products=Join-Path $SharedRoot 'products'
if ($Mode -eq 'export') {
  if (Test-Path -LiteralPath $manifest) { throw 'Manifest already exists. Use a new private output folder for a new build.' }
  New-Item -ItemType Directory -Force -Path $products | Out-Null
} else {
  if (!(Test-Path -LiteralPath $manifest) -or !(Test-Path -LiteralPath $graph)) { throw 'Export the graph into this private folder before running nodes.' }
  $old=Get-Content -LiteralPath $manifest -Raw | ConvertFrom-Json
  if ($old.signature -ne $signature) { throw 'Source revision or engine build options do not match exported graph.' }
}
$argList=@('BuildGraph','-Script=Engine/Build/InstalledEngineBuild.xml','-Target="Make Installed Build Win64"')
foreach ($item in $settings) { $argList+=('-set:' + $item) }
$argList+=@('-NoP4','-unattended')
if ($Mode -eq 'export') { $argList+=('-Export="' + $graph + '"') }
if ($Mode -eq 'node') { $argList+=('-SingleNode="' + $NodeName + '"') }
if ($Mode -ne 'export') {
  $argList+=('-SharedStorageDir="' + $products + '"')
  $argList+='-WriteToSharedStorage'
  if ($Mode -eq 'resume') { $argList+='-Resume' }
}
$out=Join-Path $env:RUNNER_TEMP 'private-buildgraph-stdout.log'
$err=Join-Path $env:RUNNER_TEMP 'private-buildgraph-stderr.log'
try {
  Write-Output "Starting licensed BuildGraph stage: $Mode. No private build logs will be uploaded."
  $proc=Start-Process -FilePath $uat -ArgumentList ($argList -join ' ') -WorkingDirectory $EngineRoot -RedirectStandardOutput $out -RedirectStandardError $err -PassThru -WindowStyle Hidden
  $deadline=(Get-Date).AddMinutes(315)
  $stop=''
  $drive=[IO.DriveInfo]::new([IO.Path]::GetPathRoot($EngineRoot))
  while (!$proc.HasExited) {
    Start-Sleep -Seconds 20
    $proc.Refresh()
    if ($drive.AvailableFreeSpace -lt 18GB) { $stop='disk-guard'; break }
    if ((Get-Date) -gt $deadline) { $stop='time-limit'; break }
  }
  if ($stop -and !$proc.HasExited) {
    & taskkill.exe /F /T /PID $proc.Id 2>$null | Out-Null
    $proc.WaitForExit(20000) | Out-Null
  }
  $proc.Refresh()
  $rc=if ($stop) { 98 } else { $proc.ExitCode }
  $priv=(@($out,$err) | Where-Object { Test-Path -LiteralPath $_ } | ForEach-Object { [IO.File]::ReadAllText($_) }) -join [Environment]::NewLine
  $codes=[regex]::Matches($priv,'\b(CS\d{4}|MSB\d{4}|NETSDK\d{4}|NU\d{4}|LNK\d{4})\b','IgnoreCase') | ForEach-Object { $_.Value.ToUpperInvariant() } | Select-Object -Unique
  $display=if($codes){$codes -join ','}else{'none'}
  Write-Output "BuildGraph stage exit=$rc; cutoff=$stop; compiler codes=$display."
  if ($rc -ne 0) { throw 'BuildGraph node did not succeed. Raw logs stay private.' }
  if ($Mode -eq 'export') {
    if (!(Test-Path -LiteralPath $graph)) { throw 'BuildGraph did not write the exported private graph.' }
    @{schema=1; signature=$signature; configuration='Win64-Android-Development'} | ConvertTo-Json | Set-Content -LiteralPath $manifest -Encoding utf8
    Write-Output 'Private exported graph and build manifest created.'
  } else { Write-Output 'BuildGraph stage succeeded; build products retained on the private persistent host.' }
}
finally {
  Remove-Item -LiteralPath $out,$err -Force -ErrorAction SilentlyContinue
}
