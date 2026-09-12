#!/usr/bin/env python3
"""Capture a short, captioned MuJoCo demo video."""
from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from robotics.so101_bimanual import SO101BimanualEnv, VisualLanguagePolicy


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("artifacts/so101_bimanual_demo.mp4"))
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--fps", type=int, default=24)
    args = parser.parse_args()
    frames = args.output.with_suffix("")
    frames.mkdir(parents=True, exist_ok=True)
    env = SO101BimanualEnv(seed=args.seed, render_width=960, render_height=540)
    policy = VisualLanguagePolicy()
    obs = env.observation()
    for index in range(96):
        frame = obs["image"]
        from PIL import Image, ImageDraw
        image = Image.fromarray(frame)
        draw = ImageDraw.Draw(image)
        draw.rectangle((16, 16, 700, 84), fill=(8, 17, 31))
        draw.text((30, 28), "PROOFDROP // SO-101 Bimanual VLA", fill=(240, 248, 255))
        draw.text((30, 52), f"seed={args.seed}  step={index:03d}  visual servoing active", fill=(93, 210, 255))
        image.save(frames / f"frame-{index:04d}.png")
        action = policy(obs["image"], obs["state"], obs["instruction"])
        obs, _, done, _ = env.step(action)
        if done and index < 95:
            for hold in range(index + 1, 96):
                image.save(frames / f"frame-{hold:04d}.png")
            break
    env.close()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-framerate", str(args.fps), "-i", str(frames / "frame-%04d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(args.output)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
