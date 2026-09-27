{{- /* chezmoi:modify-template */ -}}
{{- /* Keep the block the Coreutils installer owns; it rewrites it on every update. */ -}}
{{- with regexFind "(?s)# DO NOT MODIFY -- coreutils -- [0-9a-f-]+.*# DO NOT MODIFY -- coreutils -- [0-9a-f-]+" .chezmoi.stdin }}{{ . }}
{{ end -}}
$conda = "$env:USERPROFILE\miniforge3\Scripts\conda.exe"
if (Test-Path $conda) { (& $conda 'shell.powershell' 'hook') | Out-String | Invoke-Expression }

# Prompt. Must load after conda, which rewrites the prompt.
Invoke-Expression (&starship init powershell)
