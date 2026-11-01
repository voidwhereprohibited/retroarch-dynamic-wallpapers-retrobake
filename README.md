# RetroBake Dynamic Wallpapers for RetroArch

**10 styles · 4K (3840 × 2160) · every menu tab + 26 systems · one-click install on Windows and Linux**

RetroArch's XMB menu can change its background picture every time you move to a different
system or menu tab. This pack gives you a full set of those pictures in 10 different styles,
plus a script that downloads box art and screenshots for your games, so it all looks like this
when you scroll:

- the **system name and release year** in the top-left corner,
- see-through **frames that line up with RetroArch's icons**,
- the **box art** on the right and a **gameplay screenshot** on the left when you highlight a game.

![All styles](docs/overview.jpg)

| Style | | Style | |
|---|---|---|---|
| **Synthwave Drive** | ![](docs/previews/Synthwave%20Drive.jpg) | **Retro Neon** | ![](docs/previews/Retro%20Neon.jpg) |
| **Arcade Room** | ![](docs/previews/Arcade%20Room.jpg) | **Teal Arcade** | ![](docs/previews/Teal%20Arcade.jpg) |
| **Neon Chase** | ![](docs/previews/Neon%20Chase.jpg) | **Classic Controller** | ![](docs/previews/Classic%20Controller.jpg) |
| **Rainbow Pad** | ![](docs/previews/Rainbow%20Pad.jpg) | **Steel Claws** | ![](docs/previews/Steel%20Claws.jpg) |
| **Comic Heroes** | ![](docs/previews/Comic%20Heroes.jpg) | **Block World** | ![](docs/previews/Block%20World.jpg) |

---

## Quick install (about 2 minutes)

> **Close RetroArch first.** RetroArch saves its settings when it closes, which would undo the changes.

### Windows

1. Click the green **Code** button at the top of this page → **Download ZIP**.
2. Right-click the ZIP → **Extract All…** → **Extract**.
3. Open the extracted folder, right-click **`install.ps1`** → **Run with PowerShell**.
   - If Windows asks *"Do you want to change the execution policy?"* type **Y** and press Enter.
4. Type the number of the style you want and press **Enter**. It downloads that style (about 250 MB) and installs it.
5. When it asks about box art, press **Enter** (yes). This needs [Python](https://www.python.org/downloads/); if you don't have it, RetroArch will still fetch art while you browse.
6. Open RetroArch. Done.

### Linux (Ubuntu, Mint, Fedora, Steam Deck desktop mode…)

Open a terminal and paste:

```bash
git clone https://github.com/voidwhereprohibited/retroarch-dynamic-wallpapers-retrobake.git
```

```bash
cd retroarch-dynamic-wallpapers-retrobake && ./install.sh
```

Type the number of the style you want and press **Enter**. The installer downloads that style (about 250 MB), installs it, then asks about box art: press **Enter**. Open RetroArch. Done.

Works with the normal, **Flatpak** and **Snap** versions of RetroArch.

### What the installer changes

It copies the pictures, **backs up your `retroarch.cfg`** (as `retroarch.cfg.bak-<date>`), then sets:

| Setting (as shown in RetroArch) | Value | Why |
|---|---|---|
| Settings → Drivers → **Menu** | XMB | These pictures are made for the XMB layout |
| Settings → User Interface → Appearance → **Dynamic Background** | ON | Changes the picture per system |
| Settings → Directory → **Dynamic Backgrounds** | the style folder | Where the pictures live |
| Settings → User Interface → Appearance → **Show Title Header** | OFF | The title art sits where this text would be |
| Settings → User Interface → Appearance → **Primary Thumbnail** | Boxart | Box art on the right |
| Settings → User Interface → Appearance → **Secondary Thumbnail** | Screenshot | Gameplay picture on the left |
| Settings → Playlists → **On-Demand Thumbnail Downloads** | ON | Missing art downloads as you browse |

To undo everything, close RetroArch and rename the newest `retroarch.cfg.bak-…` back to `retroarch.cfg`.

---

## Manual install (if you'd rather click through RetroArch yourself)

1. Download one style from the [**Releases page**](https://github.com/voidwhereprohibited/retroarch-dynamic-wallpapers-retrobake/releases/latest) (for example `Synthwave-Drive.zip`), unzip it, and copy the folder into RetroArch's `wallpapers` folder:
   - **Windows:** the `wallpapers` folder next to `retroarch.exe` (usually `C:\RetroArch-Win64\wallpapers\`), or `%APPDATA%\RetroArch\wallpapers\` if your `retroarch.cfg` lives there
   - **Linux:** `~/.config/retroarch/wallpapers/`
   - **Flatpak:** `~/.var/app/org.libretro.RetroArch/config/retroarch/wallpapers/`
2. In RetroArch go to **Settings → Drivers → Menu** and pick **xmb**. Restart RetroArch if it changed.
3. **Settings → Directory → Dynamic Backgrounds** → browse to the folder from step 1 → **Use This Directory**.
4. **Settings → User Interface → Appearance**:
   - **Dynamic Background** → ON
   - **Show Title Header** → OFF
   - **Primary Thumbnail** → Boxart
   - **Secondary Thumbnail** → Screenshot
5. **Settings → Playlists → On-Demand Thumbnail Downloads** → ON.
6. Go back to the main menu and scroll left and right. The picture changes with each system.

---

## Box art and screenshots for every game

RetroArch finds art by the game's **exact official name**, like `Sonic The Hedgehog (USA, Europe)`.
If your games have short names like `Sonic the Hedgehog`, RetroArch shows nothing.
`scripts/fetch_thumbnails.py` fixes that: it matches every game in your playlists to the official
name and saves the art under **your** name.

```bash
python3 scripts/fetch_thumbnails.py
```

On Windows use `py scripts\fetch_thumbnails.py`. It reads your RetroArch settings to find your
playlists, needs no account, and can be run again any time you add games (it skips what you already have).

---

## Your playlists must have the standard names

Pictures are matched by **file name = playlist name**. RetroArch's **Import Content → Scan Directory**
creates the standard names automatically (for example `Nintendo - Super Nintendo Entertainment System`).
If you made a playlist yourself, rename it to the standard name in
**Settings → Playlists → Manage Playlists**, or rename the picture to match your playlist.

Included names (alternate names like `Nintendo - Super Famicom` are included as copies):

<details><summary>Show all 37 names</summary>

Menu tabs: Main Menu, Settings, History, Favorites, Netplay, Import Content, Explore, Images, Music, Videos, 00 - Generic Background

Systems: Nintendo Entertainment System, Super Nintendo, Nintendo 64, GameCube, Wii, Game Boy, Game Boy Color,
Game Boy Advance, Nintendo DS, Nintendo 3DS, Virtual Boy, Mega Drive / Genesis, 32X, Mega-CD / Sega CD,
Master System, Game Gear, Saturn, Dreamcast, PlayStation, PlayStation 2, PSP, Atari 2600, Atari Lynx,
PC Engine / TurboGrafx-16, Neo Geo, Arcade (MAME, FBNeo)
</details>

**Using RetroArch in another language?** The menu-tab pictures use the English names
(`Main Menu`, `Settings`…). Rename those to what your RetroArch shows.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| The picture never changes | Settings → User Interface → Appearance → **Dynamic Background** must be ON, and the menu must be **XMB**. |
| One system shows the plain background | Its playlist name doesn't match a picture. See *Your playlists must have the standard names*. |
| My settings went back to how they were | RetroArch was open while installing. Close it and run the installer again. |
| No box art | Run `fetch_thumbnails.py`, and check **Primary Thumbnail** is set to Boxart. |
| Text overlaps the title | Turn **Show Title Header** OFF. |
| Everything looks small or huge | Settings → User Interface → Appearance → **Menu Scale Factor** → 1.00x. |

---

## Make your own style

Everything is generated by `scripts/build.py` from two small files:

- `scripts/styles.json` - one art prompt + lettering style per theme
- `scripts/systems.json` - the systems, their release years and a plain description of the hardware

```bash
python3 scripts/build.py --styles synthwave-drive
```

Art is generated with the free [Pollinations](https://pollinations.ai) API and sharpened to 4K with
[Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN). Raw art goes to `backgrounds/`, finished pictures to `dist/`.

---

## Credits and license

- Made by [voidwhereprohibited](https://github.com/voidwhereprohibited) for the RetroBake project.
- Inspired by [RetroPlayer](https://github.com/morlenxus/retroarch-dynamic-wallpapers-retroplayer) by Brian 'morlenxus' Miculcy and the Shakabello dynamic wallpapers.
- Artwork: original, AI-generated. No logos or characters; system names are used only to say which console a picture is for.
- Fonts: Google Fonts (SIL Open Font License) and DejaVu. See `fonts/`.
- **Pictures:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). **Scripts:** MIT.
- Box art downloaded by `fetch_thumbnails.py` comes from [libretro-thumbnails](https://github.com/libretro-thumbnails/libretro-thumbnails) and is not part of this repo.

All console names are trademarks of their owners. This project is not affiliated with Nintendo, Sega, Sony, Atari, NEC, SNK or libretro.
