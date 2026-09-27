$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$file = 'CascadiaMonoNF.ttf'
$userReg = 'HKCU:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts'
$installed = 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts', $userReg |
    Where-Object { (Get-ItemProperty $_ -ErrorAction SilentlyContinue).PSObject.Properties.Value -like "*$file" }
if ($installed) { return }

# Cascadia is not on winget; the release zip is pinned and hash-checked.
$version = '2407.24'
$zip = Join-Path $env:TEMP "CascadiaCode-$version.zip"
Invoke-WebRequest "https://github.com/microsoft/cascadia-code/releases/download/v$version/CascadiaCode-$version.zip" -OutFile $zip
if ((Get-FileHash $zip).Hash -ne 'E67A68EE3386DB63F48B9054BD196EA752BC6A4EBB4DF35ADCE6733DA50C8474') {
    throw "Cascadia zip hash mismatch"
}

$dir = Join-Path $env:LOCALAPPDATA 'Microsoft\Windows\Fonts'
New-Item -ItemType Directory $dir -Force | Out-Null
Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [IO.Compression.ZipFile]::OpenRead($zip)
try {
    $entry = $archive.Entries | Where-Object Name -eq $file
    [IO.Compression.ZipFileExtensions]::ExtractToFile($entry, (Join-Path $dir $file), $true)
} finally {
    $archive.Dispose()
}
Remove-Item $zip
New-ItemProperty $userReg -Name 'Cascadia Mono NF (TrueType)' -Value (Join-Path $dir $file) -Force | Out-Null
