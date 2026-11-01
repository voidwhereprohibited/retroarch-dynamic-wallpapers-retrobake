# RetroBake Dynamic Wallpapers - Windows installer
# Right-click this file > "Run with PowerShell"   (or:  powershell -ExecutionPolicy Bypass -File install.ps1)
$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Find RetroArch's config folder (installer version, portable version, Steam version)
$cands = @("$env:APPDATA\RetroArch", "C:\RetroArch-Win64", "C:\RetroArch",
           "${env:ProgramFiles(x86)}\Steam\steamapps\common\RetroArch", "$env:ProgramFiles\RetroArch")
$Cfg = $cands | Where-Object { Test-Path "$_\retroarch.cfg" } | Select-Object -First 1
if (-not $Cfg) {
  $Cfg = Read-Host "Could not find retroarch.cfg. Paste the folder where RetroArch is installed"
  if (-not (Test-Path "$Cfg\retroarch.cfg")) { Write-Host "No retroarch.cfg there. Start RetroArch once, close it, and try again."; pause; exit 1 }
}
Write-Host "RetroArch config: $Cfg"

# 2. RetroArch must be closed
if (Get-Process retroarch -ErrorAction SilentlyContinue) { Write-Host "Please close RetroArch first, then run this again."; pause; exit 1 }

# 3. Pick a style
$styles = @("Synthwave Drive", "Retro Neon", "Arcade Room", "Teal Arcade", "Neon Chase", "Classic Controller", "Rainbow Pad", "Steel Claws", "Comic Heroes", "Block World")
for ($i = 0; $i -lt $styles.Count; $i++) { Write-Host ("  {0,2}) {1}" -f ($i + 1), $styles[$i]) }
$n = [int](Read-Host "Pick a style number")
$Style = $styles[$n - 1]

if (-not (Test-Path "$Here\dist\$Style")) {
  $zip = ($Style -replace ' ', '-') + ".zip"
  Write-Host "Downloading $Style ..."
  New-Item -ItemType Directory -Force -Path "$Here\dist" | Out-Null
  [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
  $ProgressPreference = 'SilentlyContinue'
  Invoke-WebRequest "https://github.com/voidwhereprohibited/retroarch-dynamic-wallpapers-retrobake/releases/latest/download/$zip" -OutFile "$Here\dist\$zip"
  Expand-Archive "$Here\dist\$zip" -DestinationPath "$Here\dist" -Force
  Remove-Item "$Here\dist\$zip"
}

# 4. Copy the wallpapers
$Dest = "$Cfg\wallpapers\RetroBake - $Style"
New-Item -ItemType Directory -Force -Path $Dest | Out-Null
Copy-Item "$Here\dist\$Style\*.png" $Dest -Force
Write-Host "Copied $((Get-ChildItem $Dest).Count) wallpapers to $Dest"

# 5. Back up retroarch.cfg, then turn on the settings this pack needs
$file = "$Cfg\retroarch.cfg"
Copy-Item $file "$file.bak-$(Get-Date -Format yyyyMMdd-HHmmss)"
$lines = [System.Collections.ArrayList]@(Get-Content $file)
function Set-Cfg($key, $value) {
  $line = "$key = `"$value`""
  $idx = -1; for ($j = 0; $j -lt $lines.Count; $j++) { if ($lines[$j] -match "^$([regex]::Escape($key)) = ") { $idx = $j } }
  if ($idx -ge 0) { $lines[$idx] = $line } else { [void]$lines.Add($line) }
}
Set-Cfg "menu_driver" "xmb"
Set-Cfg "menu_dynamic_wallpaper_enable" "true"
Set-Cfg "dynamic_wallpapers_directory" $Dest
Set-Cfg "menu_wallpaper" ""
Set-Cfg "menu_xmb_show_title_header" "false"
Set-Cfg "menu_thumbnails" "3"
Set-Cfg "menu_left_thumbnails" "1"
Set-Cfg "network_on_demand_thumbnails" "true"
Set-Content -Path $file -Value $lines -Encoding ASCII
Write-Host "Settings updated (backup saved next to retroarch.cfg)."

# 6. Optional: box art + screenshots for your games (needs Python from python.org or the Microsoft Store)
$yn = Read-Host "Download box art and screenshots for your games now? [Y/n]"
if ($yn -ne "n") {
  $py = Get-Command py -ErrorAction SilentlyContinue
  if (-not $py) { $py = Get-Command python -ErrorAction SilentlyContinue }
  if ($py) { & $py.Source "$Here\scripts\fetch_thumbnails.py" } else { Write-Host "Python not found - skipped. RetroArch will still download art as you browse (on-demand thumbnails are on)." }
}
Write-Host "`nDone! Open RetroArch."; pause
