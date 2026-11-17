$ErrorActionPreference = 'Stop'

if (Get-Command ocr -ErrorAction SilentlyContinue) { return }
$npm = Get-Command npm.cmd -ErrorAction Stop
& $npm.Source install -g '@alibaba-group/open-code-review@1.13.10'
if ($LASTEXITCODE -ne 0) { throw 'Open Code Review installation failed' }
