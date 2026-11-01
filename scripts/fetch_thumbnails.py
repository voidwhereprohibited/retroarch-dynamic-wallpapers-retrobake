#!/usr/bin/env python3
"""Download box art, title screens and gameplay snaps for every game in your RetroArch playlists,
even when your games have short clean names (e.g. "Sonic the Hedgehog" instead of
"Sonic The Hedgehog (USA, Europe)"). Matches each playlist label to the official libretro-thumbnails
name, then saves the images under YOUR label so RetroArch shows them.

Usage:  python3 fetch_thumbnails.py [--playlists DIR] [--thumbnails DIR]
Defaults read from your retroarch.cfg (Linux: ~/.config/retroarch, Windows: %APPDATA%\\RetroArch).
No account or key needed. Python 3.8+ only, no extra packages.
"""
import argparse, json, os, re, sys, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

TYPES = ("Named_Boxarts", "Named_Titles", "Named_Snaps")
SERVER = "https://thumbnails.libretro.com"
REGION = ["(usa", "(world", "(usa, europe", "(europe", "(japan"]


def cfg_dir():
    if os.name == "nt":
        for p in (Path(os.environ.get("APPDATA", "")) / "RetroArch", Path("C:/RetroArch-Win64")):
            if (p / "retroarch.cfg").exists():
                return p
    for p in (Path.home() / ".config/retroarch", Path.home() / ".var/app/org.libretro.RetroArch/config/retroarch",
              Path.home() / "snap/retroarch/current/.config/retroarch"):
        if (p / "retroarch.cfg").exists():
            return p
    sys.exit("Could not find retroarch.cfg - pass --playlists and --thumbnails")


def cfg_get(cfg, key, default):
    m = re.search(rf'^{key}\s*=\s*"(.*)"', cfg, re.M)
    v = m.group(1) if m and m.group(1) not in ("", "default") else default
    return Path(os.path.expanduser(v.replace(":\\", ":/") if os.name == "nt" else v))


def norm(s):
    s = re.sub(r"\s*[\(\[][^\)\]]*[\)\]]", "", s).lower().replace("&", "and")
    m = re.match(r"^(.*), (the|a|an)$", s.strip())
    if m:
        s = f"{m.group(2)} {m.group(1)}"
    return re.sub(r"[^a-z0-9]", "", s)


def safe(label):
    return re.sub(r'[&*/:`<>?\\|"]', "_", label)


def listing(system):
    """Names available on the libretro thumbnail server for one system (boxart folder)."""
    url = f"{SERVER}/{urllib.parse.quote(system)}/Named_Boxarts/"
    try:
        html = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "rb-thumbs"}), timeout=60).read().decode("utf-8", "ignore")
    except Exception as e:
        print(f"  ! no thumbnail index for {system}: {e}"); return {}
    names = [urllib.parse.unquote(h)[:-4] for h in re.findall(r'href="([^"?/][^"]*\.png)"', html)]
    best = {}
    for n in names:
        k = norm(n)
        rank = next((i for i, r in enumerate(REGION) if n.lower().find(r) >= 0), 9)
        if k not in best or rank < best[k][0]:
            best[k] = (rank, n)
    return {k: v[1] for k, v in best.items()}


def get(url, dest):
    if dest.exists():
        return "skip"
    try:
        data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "rb-thumbs"}), timeout=60).read()
        dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(data); return "ok"
    except Exception:
        return "miss"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--playlists"); ap.add_argument("--thumbnails"); a = ap.parse_args()
    c = cfg_dir(); cfg = (c / "retroarch.cfg").read_text(errors="ignore")
    pl = Path(a.playlists) if a.playlists else cfg_get(cfg, "playlist_directory", str(c / "playlists"))
    th = Path(a.thumbnails) if a.thumbnails else cfg_get(cfg, "thumbnails_directory", str(c / "thumbnails"))
    print(f"playlists: {pl}\nthumbnails: {th}")
    for f in sorted(pl.glob("*.lpl")):
        system = f.stem
        items = json.loads(f.read_text(encoding="utf-8")).get("items", [])
        idx = listing(system)
        jobs, matched = [], 0
        for it in items:
            label = it.get("label") or Path(it["path"].split("#")[0]).stem
            off = idx.get(norm(label))
            if not off:
                continue
            matched += 1
            for t in TYPES:
                jobs.append((f"{SERVER}/{urllib.parse.quote(system)}/{t}/{urllib.parse.quote(safe(off))}.png",
                             th / system / t / f"{safe(label)}.png"))
        with ThreadPoolExecutor(8) as ex:
            res = list(ex.map(lambda j: get(*j), jobs))
        print(f"{system}: {matched}/{len(items)} games matched, {res.count('ok')} downloaded, {res.count('skip')} already had")


if __name__ == "__main__":
    main()
