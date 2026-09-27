$ErrorActionPreference = 'Stop'

# UAC elevation runs as the same account, so HKCU below is still this user's hive.
$principal = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    $shell = (Get-Process -Id $PID).Path
    $p = Start-Process $shell -Verb RunAs -Wait -PassThru -ArgumentList '-NoProfile', '-File', "`"$PSCommandPath`""
    exit $p.ExitCode
}

$explorer = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer'
$advanced = "$explorer\Advanced"
$settings = @(
    # Explorer
    @($advanced, 'HideFileExt', 0),
    @($advanced, 'Hidden', 1),
    @("$explorer\CabinetState", 'FullPath', 1),
    @($advanced, 'LaunchTo', 1),
    @($explorer, 'ShowFrequent', 0),
    @($explorer, 'ShowRecent', 0),
    @($explorer, 'ShowCloudFilesInQuickAccess', 0),
    @($advanced, 'ShowSyncProviderNotifications', 0),
    @("$explorer\Modules\GlobalSettings\DetailsContainer", 'DetailsContainer', [byte[]](1, 0, 0, 0, 2, 0, 0, 0), 'Binary'),
    # Taskbar, Start, search, notifications
    @('HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Notifications\Settings', 'NOC_GLOBAL_SETTING_TOASTS_ENABLED', 0),
    @('HKCU:\Control Panel\Bluetooth', 'Notification Area Icon', 0),
    @("$advanced\TaskbarDeveloperSettings", 'TaskbarEndTask', 1),
    @('HKCU:\SOFTWARE\Policies\Microsoft\Windows\Explorer', 'DisableSearchBoxSuggestions', 1),
    @('HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\SearchSettings', 'IsDynamicSearchBoxEnabled', 0),
    @($advanced, 'Start_IrisRecommendations', 0),
    @($advanced, 'Start_AccountNotifications', 0),
    @('HKLM:\SOFTWARE\Policies\Microsoft\Dsh', 'AllowNewsAndInterests', 0),
    # Theme
    @('HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize', 'AppsUseLightTheme', 0),
    @('HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize', 'SystemUsesLightTheme', 0),
    # System
    @('HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Sudo', 'Enabled', 3),
    @('HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock', 'AllowDevelopmentWithoutDevLicense', 1),
    @('HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem', 'LongPathsEnabled', 1),
    @('HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server', 'fDenyTSConnections', 1),
    # Edge
    @('HKLM:\SOFTWARE\Policies\Microsoft\Edge', 'NewTabPageLocation', 'about:blank', 'String'),
    @('HKLM:\SOFTWARE\Policies\Microsoft\Edge', 'HideFirstRunExperience', 1)
)

$failed = 0
foreach ($s in $settings) {
    $path, $name, $value, $type = $s
    if (-not $type) { $type = 'DWord' }
    # Skip values already set: some keys, e.g. the Widgets policy, deny writes even to admins.
    if ("$((Get-ItemProperty $path -Name $name -ErrorAction SilentlyContinue).$name)" -eq "$value") { continue }
    try {
        # New-Item -Force on an existing key would wipe its values, so only create missing keys.
        if (-not (Test-Path $path)) { New-Item $path -Force | Out-Null }
        New-ItemProperty $path -Name $name -Value $value -PropertyType $type -Force | Out-Null
    } catch {
        Write-Warning "${path}\${name}: $($_.Exception.Message)"
        $failed++
    }
}
# The elevated window closes on exit, so hold it open to show the warnings.
if ($failed) { Read-Host "$failed setting(s) failed, see above. Press Enter to close" }
exit [int]($failed -gt 0)
