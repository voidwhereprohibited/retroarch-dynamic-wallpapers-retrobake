#!/usr/bin/env python3
"""Build RetroBake dynamic wallpapers.

1. generate artwork per style x (system | tab) with Pollinations (free; key optional) -> backgrounds/<style>/<name>.png
2. upscale 2x with Real-ESRGAN -> 3840x2160
3. compose: XMB-aligned overlay frame + styled title + "Released" line -> dist/<Style>/<playlist name>.png
   (+ copies for alternative playlist names)

Usage: build.py [--styles a,b] [--only "Name1|Name2"] [--no-gen]
Env:   POLLINATIONS_KEY or ~/.config/retrobake/pollinations.key ; ESRGAN=path to realesrgan-ncnn-vulkan
"""
import argparse, io, json, os, shutil, subprocess, sys, tempfile, time, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import lettering as L

W, H = 3840, 2160
FONTS = ROOT / "fonts"
ESRGAN = Path(os.environ.get("ESRGAN", Path.home() / "Projects/retrobake/.tools/realesrgan/realesrgan-ncnn-vulkan"))
MODEL = os.environ.get("RB_MODEL", "black-forest-labs/flux.1-schnell")
GW, GH = int(os.environ.get("RB_W", 1280)), int(os.environ.get("RB_H", 768))
SCALE = os.environ.get("RB_SCALE", "3")


def key():
    k = os.environ.get("POLLINATIONS_KEY")
    f = Path.home() / ".config/retrobake/pollinations.key"
    return k or (f.read_text().strip() if f.exists() else None)


def generate(prompt, seed, dest):
    if dest.exists():
        return dest
    k = key()
    q = urllib.parse.quote(prompt[:1800], safe="")
    if k:
        url = f"https://gen.pollinations.ai/image/{q}?" + urllib.parse.urlencode(
            {"model": MODEL, "width": GW, "height": GH, "seed": seed, "nologo": "true", "safe": "true"})
        hdr = {"Authorization": f"Bearer {k}"}
    else:
        url = f"https://image.pollinations.ai/prompt/{q}?" + urllib.parse.urlencode(
            {"width": GW, "height": GH, "seed": seed, "nologo": "true"})
        hdr = {}
    for attempt in range(10):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "RetroBake-wallpapers", **hdr})
            with urllib.request.urlopen(req, timeout=240) as r:
                im = Image.open(io.BytesIO(r.read())).convert("RGB")
            dest.parent.mkdir(parents=True, exist_ok=True)
            im.save(dest)
            return dest
        except Exception as e:
            print(f"   retry {attempt + 1}: {e}", flush=True)
            time.sleep(15 if k else 50)
    raise SystemExit(f"failed: {dest}")


def cover(im, w, h):
    s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def upscale(src):
    s = "2" if Image.open(src).width >= 1900 else SCALE
    out = src.with_name(src.stem + f".x{s}.png")
    if not out.exists():
        subprocess.run([str(ESRGAN), "-i", str(src), "-o", str(out), "-n", "realesr-animevideov3", "-s", s],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return cover(Image.open(out).convert("RGB"), W, H)


def rgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def overlay(im, accent):
    """XMB-aligned frame (proportions measured from RetroArch XMB at default scale)."""
    a = rgb(accent)
    lay = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(lay)
    hy0, hy1 = int(H * .215), int(H * .289)          # icon-row band
    vx0, vx1 = int(W * .279), int(W * .299)          # selected-column band
    d.rectangle((0, hy0, W, hy1), fill=(0, 0, 0, 90))
    d.rectangle((vx0, 0, vx1, H), fill=(0, 0, 0, 90))
    for y in (hy0, hy1):
        d.rectangle((0, y - 2, W, y + 2), fill=a + (150,))
    for x in (vx0, vx1):
        d.rectangle((x - 2, 0, x + 2, H), fill=a + (150,))
    for bx0, by0, bx1, by1 in ((.227, .178, .332, .326), (.239, .364, .319, .493)):
        box = (int(W * bx0), int(H * by0), int(W * bx1), int(H * by1))
        d.rectangle(box, fill=(0, 0, 0, 120))
        d.rectangle(box, outline=a + (215,), width=5)
    im.alpha_composite(lay)
    # soften the top-left so the title always reads
    g = Image.linear_gradient("L").rotate(90).resize((W, int(H * .2))).point(lambda v: int(v * .55))
    tl = Image.new("RGBA", (W, int(H * .2)), (0, 0, 0, 0)); tl.putalpha(g.transpose(Image.FLIP_LEFT_RIGHT))
    tl.putalpha(Image.eval(tl.getchannel("A"), lambda v: v))
    im.alpha_composite(tl)


def compose(bg, title, year, style):
    im = bg.convert("RGBA")
    overlay(im, style["accent"])
    if title:
        L.place(im, title, style["letter"], FONTS, x=70, y=55, maxw=int(W * .30), maxh=int(H * .085))
    if year:
        f = ImageFont.truetype(str(FONTS / "DejaVuSansMono-Bold.ttf"), 64)
        d = ImageDraw.Draw(im)
        d.text((134, int(H * .145) + 4), f"Released: {year}", font=f, fill=(0, 0, 0, 230))
        d.text((130, int(H * .145)), f"Released: {year}", font=f, fill=(245, 240, 230, 255))
    return im.convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--styles", default=""); ap.add_argument("--only", default=""); ap.add_argument("--no-gen", action="store_true")
    a = ap.parse_args()
    S = json.loads((ROOT / "scripts/styles.json").read_text()); Y = json.loads((ROOT / "scripts/systems.json").read_text())
    jobs = [(n, v["hw"], v.get("short"), v.get("year"), v.get("alt", [])) for n, v in Y["systems"].items()]
    jobs += [(n, desc, (n if n != "00 - Generic Background" else ""), None, []) for n, desc in Y["tabs"].items()]
    only = set(filter(None, a.only.split("|")))
    for sid, st in S["styles"].items():
        if a.styles and sid not in a.styles.split(","):
            continue
        out = ROOT / "dist" / st["name"]; out.mkdir(parents=True, exist_ok=True)
        for i, (name, subj, title, year, alts) in enumerate(jobs):
            if only and name not in only:
                continue
            t0 = time.time()
            raw = ROOT / "backgrounds" / sid / f"{name}.png"
            if not a.no_gen:
                generate(st["prompt"].format(subject=subj) + " " + S["template_tail"], st["seed"] + i, raw)
            img = compose(upscale(raw), title, year, st)
            img.save(out / f"{name}.png", optimize=False, compress_level=6)
            for alt in alts:
                shutil.copyfile(out / f"{name}.png", out / f"{alt}.png")
            print(f"{st['name']:18} {name}  ({time.time() - t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
