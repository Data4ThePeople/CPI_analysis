"""Social GIF: the balloon rising and falling, October 2016 to the release month.

One frame per published month from dist/over-time.html in its #gif mode, drawn
in about 8 seconds, then the release month held for 5 seconds. Every frame is a
real month; nothing is interpolated. The last frame is the published page's
release month. Writes posts/<slug>/social/<slug>-balloon.gif.
"""
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

from common import DIST, PROCESSED, ROOT, SLUG

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CSS_W, CSS_H, SCALE = 600, 750, 1.4      # 4:5, the feed shape on LinkedIn and X
OUT_W, OUT_H = 640, 800
DRAW_S, HOLD_MS = 8.0, 5000


def frame(month: str, path: Path):
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    f"--window-size={CSS_W},{CSS_H}", f"--force-device-scale-factor={SCALE}",
                    "--virtual-time-budget=3000", f"--screenshot={path}",
                    f"file://{DIST / 'over-time.html'}#gif&theme=light&month={month}"],
                   capture_output=True, timeout=120, check=True)


def main():
    order = json.loads((PROCESSED / "over-time_data.json").read_text())["order"]
    out_dir = ROOT / "posts" / SLUG / "social"
    out_dir.mkdir(parents=True, exist_ok=True)
    frames = []
    with tempfile.TemporaryDirectory() as tmp:
        for k, m in enumerate(order):
            p = Path(tmp) / f"{k:03d}.png"
            frame(m, p)
            frames.append(Image.open(p).convert("RGB").resize((OUT_W, OUT_H), Image.LANCZOS))
            print(m, end=" ", flush=True)
    print()
    # One palette for every frame, taken from the last frame, so colors do not flicker.
    pal = frames[-1].quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    step = max(20, round(DRAW_S * 1000 / len(q) / 10) * 10)
    durations = [step] * (len(q) - 1) + [HOLD_MS]
    out = out_dir / f"{SLUG}-balloon.gif"
    q[0].save(out, save_all=True, append_images=q[1:], duration=durations, loop=0, optimize=True, disposal=1)
    print("wrote", out.relative_to(ROOT), f"{out.stat().st_size / 1e6:.1f} MB,", len(q), "frames,",
          f"{step} ms each, last held {HOLD_MS / 1000:.0f} s")


if __name__ == "__main__":
    main()
