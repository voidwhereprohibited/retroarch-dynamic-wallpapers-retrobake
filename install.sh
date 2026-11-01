#!/usr/bin/env bash
# RetroBake Dynamic Wallpapers - Linux installer
# Usage: ./install.sh                 (asks which style)
#        ./install.sh "Synthwave Drive"
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"

# 1. Find RetroArch's config folder (native, Flatpak, Snap)
CFG=""
for d in "$HOME/.config/retroarch" "$HOME/.var/app/org.libretro.RetroArch/config/retroarch" "$HOME/snap/retroarch/current/.config/retroarch"; do
  [ -f "$d/retroarch.cfg" ] && { CFG="$d"; break; }
done
[ -z "$CFG" ] && { echo "Could not find retroarch.cfg. Start RetroArch once, close it, then run this again."; exit 1; }
echo "RetroArch config: $CFG"

# 2. RetroArch must be closed (it rewrites its config when it exits)
if pgrep -x retroarch >/dev/null 2>&1; then
  echo "Please close RetroArch first, then run this again."; exit 1
fi

# 3. Pick a style
STYLES=("Synthwave Drive" "Retro Neon" "Arcade Room" "Teal Arcade" "Neon Chase" "Classic Controller" "Rainbow Pad" "Steel Claws" "Comic Heroes" "Block World")
STYLE="${1:-}"
if [ -z "$STYLE" ]; then
  echo; echo "Pick a style:"
  for i in "${!STYLES[@]}"; do printf "  %2d) %s\n" "$((i+1))" "${STYLES[$i]}"; done
  read -rp "Number: " n; STYLE="${STYLES[$((n-1))]}"
fi
if [ ! -d "$HERE/dist/$STYLE" ]; then
  ZIP="${STYLE// /-}.zip"
  echo "Downloading $STYLE ..."
  mkdir -p "$HERE/dist"
  curl -fL --progress-bar "https://github.com/voidwhereprohibited/retroarch-dynamic-wallpapers-retrobake/releases/latest/download/$ZIP" -o "$HERE/dist/$ZIP" || { echo "Download failed. Check your internet connection."; exit 1; }
  python3 -c "import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "$HERE/dist/$ZIP" "$HERE/dist" && rm -f "$HERE/dist/$ZIP"
fi
[ -d "$HERE/dist/$STYLE" ] || { echo "Unknown style: $STYLE"; exit 1; }

# 4. Copy the wallpapers
DEST="$CFG/wallpapers/RetroBake - $STYLE"
mkdir -p "$DEST"; cp -f "$HERE/dist/$STYLE/"*.png "$DEST/"
echo "Copied $(ls "$DEST" | wc -l) wallpapers to $DEST"

# 5. Back up retroarch.cfg, then turn on the settings this pack needs
cp "$CFG/retroarch.cfg" "$CFG/retroarch.cfg.bak-$(date +%Y%m%d-%H%M%S)"
set_cfg() { # key value
  if grep -q "^$1 = " "$CFG/retroarch.cfg"; then
    sed -i "s|^$1 = .*|$1 = \"$2\"|" "$CFG/retroarch.cfg"
  else
    echo "$1 = \"$2\"" >> "$CFG/retroarch.cfg"
  fi
}
set_cfg menu_driver "xmb"
set_cfg menu_dynamic_wallpaper_enable "true"
set_cfg dynamic_wallpapers_directory "$DEST"
set_cfg menu_wallpaper ""
set_cfg menu_xmb_show_title_header "false"   # our title art sits where the header text would be
set_cfg menu_thumbnails "3"                  # right side: box art
set_cfg menu_left_thumbnails "1"             # left side: gameplay screenshot
set_cfg network_on_demand_thumbnails "true"
echo "Settings updated (backup saved next to retroarch.cfg)."

# 6. Optional: download box art + screenshots for your games
read -rp "Download box art and screenshots for your games now? [Y/n] " yn
if [ "${yn:-Y}" != "n" ] && [ "${yn:-Y}" != "N" ]; then python3 "$HERE/scripts/fetch_thumbnails.py"; fi
echo; echo "Done! Open RetroArch."
