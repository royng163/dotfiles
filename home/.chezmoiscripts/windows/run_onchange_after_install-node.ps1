$ErrorActionPreference = 'Stop'

# nvm-windows prints nothing unless attached to a console, so state is read from its folders.
$nvmHome = [Environment]::GetEnvironmentVariable('NVM_HOME', 'User')
$symlink = [Environment]::GetEnvironmentVariable('NVM_SYMLINK', 'User')
if (Test-Path $symlink) { return }

$lts = ((Invoke-RestMethod https://nodejs.org/dist/index.json) | Where-Object lts | Select-Object -First 1).version
$nvm = Join-Path $nvmHome 'nvm.exe'
& $nvm install $lts.TrimStart('v')
# The symlink needs admin, so nvm creates it in its own elevated process; wait for it.
& $nvm use $lts.TrimStart('v')
for ($i = 0; -not (Test-Path $symlink) -and $i -lt 60; $i++) { Start-Sleep 1 }
if (-not (Test-Path $symlink)) { throw "nvm use $lts did not activate Node" }
