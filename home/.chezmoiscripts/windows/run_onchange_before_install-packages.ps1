$ErrorActionPreference = 'Stop'

$packages = @(
    'Microsoft.WindowsTerminal'
    'Microsoft.PowerShell'
    'Git.Git'
    'Starship.Starship'
    'twpayne.chezmoi'
    'Microsoft.Coreutils'
    'ZedIndustries.Zed'
    'CoreyButler.NVMforWindows'
    'CondaForge.Miniforge3'
)

foreach ($id in $packages) {
    winget list --id $id --exact --accept-source-agreements --disable-interactivity *> $null
    if ($LASTEXITCODE -eq 0) { continue }
    winget install --id $id --exact --silent --accept-package-agreements --accept-source-agreements --disable-interactivity
    if ($LASTEXITCODE -ne 0) { throw "winget install $id failed with exit code $LASTEXITCODE" }
}
