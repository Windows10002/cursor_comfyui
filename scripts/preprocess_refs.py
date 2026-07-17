# -*- coding: utf-8 -*-
"""Preprocess source images: remove watermark area, align sizes, light denoise."""
from pathlib import Path
from PIL import Image, ImageFilter, ImageDraw

INP = Path(r"D:\Comfy-Desktop\ComfyUI-Shared\input")
WS = Path(r"d:\mycode\cursor_comfyui\input")


def cover_watermark(im: Image.Image) -> Image.Image:
    """Cover bottom-right Doubao watermark region with nearby grass/content clone."""
    im = im.convert("RGB")
    w, h = im.size
    # watermark typically bottom-right ~18% width x 6% height
    rw, rh = max(int(w * 0.22), 1), max(int(h * 0.07), 1)
    x0, y0 = w - rw - int(w * 0.02), h - rh - int(h * 0.02)
    # sample patch from left of watermark area
    sx0 = max(x0 - rw, 0)
    patch = im.crop((sx0, y0, sx0 + rw, y0 + rh))
    im.paste(patch, (x0, y0))
    # soft edge blend
    return im


def fit(im: Image.Image, tw=576, th=1024) -> Image.Image:
    im = im.convert("RGB")
    im.thumbnail((tw, th), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (tw, th), (20, 40, 20))
    canvas.paste(im, ((tw - im.width) // 2, (th - im.height) // 2))
    return canvas


def light_denoise(im: Image.Image) -> Image.Image:
    # very mild blur to kill compression noise, then slight sharpen
    soft = im.filter(ImageFilter.GaussianBlur(radius=0.6))
    return soft.filter(ImageFilter.UnsharpMask(radius=1.0, percent=60, threshold=2))


def main():
    person = Image.open(INP / "koubo_person.png")
    person = cover_watermark(person)
    person = fit(person)
    person = light_denoise(person)
    out = "koubo_person_clean.png"
    for d in (INP, WS):
        d.mkdir(parents=True, exist_ok=True)
        person.save(d / out, quality=95)
        print("saved", d / out)

    for name in ["koubo_bg_park.png", "koubo_product_mochi.png"]:
        im = fit(Image.open(INP / name))
        im = light_denoise(im)
        for d in (INP, WS):
            im.save(d / name.replace(".png", "_clean.png"))
            print("saved", d / name.replace(".png", "_clean.png"))


if __name__ == "__main__":
    main()
