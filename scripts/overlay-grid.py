# -*- coding: utf-8 -*-
"""overlay-grid.py — computer_use 截图 + 坐标网格叠层（v1）

把一张 computer_use 截图叠上"透明网格图层"（细线 25px / 粗线 100px + 坐标刻度），
输出与截图同尺寸的新图。vision 模型即可读出目标 UI 的网格坐标（= 截图像素坐标 =
传给 computer_use 的 coordinate 同一坐标系）。

用法:
  python3 overlay-grid.py input.png [--out output.png] [--mark x y] [--minor 25] [--major 100]
  --mark: 额外打上红色十字准星+圈，用于验证网格读数是否与真实坐标一致（校准用）。
"""
import argparse
import os
from PIL import Image, ImageDraw, ImageFont

FONT = r'C:\Windows\Fonts\consola.ttf'

def load_font(size):
    try:
        return ImageFont.truetype(FONT, size)
    except Exception:
        try:
            return ImageFont.truetype('arial.ttf', size)
        except Exception:
            return ImageFont.load_default(size=size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('input')
    ap.add_argument('--out')
    ap.add_argument('--mark', nargs=2, type=int, metavar=('X', 'Y'))
    ap.add_argument('--minor', type=int, default=25)
    ap.add_argument('--major', type=int, default=100)
    a = ap.parse_args()

    img = Image.open(a.input).convert('RGBA')
    w, h = img.size

    # 网格图层（透明底 + 半透明线条）
    grid = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(grid)
    fp = load_font(12)

    for x in range(0, w, a.minor):
        if x % a.major == 0:
            d.line([(x, 0), (x, h)], fill=(255, 80, 80, 150), width=1)  # 主轴红
        else:
            d.line([(x, 0), (x, h)], fill=(255, 255, 255, 40), width=1)

    for y in range(0, h, a.minor):
        if y % a.major == 0:
            d.line([(0, y), (w, y)], fill=(255, 80, 80, 150), width=1)
        else:
            d.line([(0, y), (w, y)], fill=(255, 255, 255, 40), width=1)

    # 坐标刻度数字（顶部 x 轴 + 左侧 y 轴，每 100px，白底黑字）
    for x in range(0, w, a.major):
        txt = str(x)
        bbox = d.textbbox((0, 0), txt, font=fp)
        tw = bbox[2] - bbox[0]
        d.rectangle([x + 2, 2, x + 2 + tw + 4, 20], fill=(255, 255, 255, 200))
        d.text((x + 4, 4), txt, fill=(0, 0, 0, 255), font=fp)
    for y in range(0, h, a.major):
        txt = str(y)
        bbox = d.textbbox((0, 0), txt, font=fp)
        tw = bbox[2] - bbox[0]
        d.rectangle([2, y + 2, 2 + tw + 4, y + 22], fill=(255, 255, 255, 200))
        d.text((4, y + 5), txt, fill=(0, 0, 0, 255), font=fp)

    # 校准标记：红圈 + 十字
    if a.mark:
        mx, my = a.mark
        d.ellipse([mx - 18, my - 18, mx + 18, my + 18], outline=(255, 0, 0, 255), width=3)
        d.line([(mx - 30, my), (mx + 30, my)], fill=(255, 0, 0, 255), width=2)
        d.line([(mx, my - 30), (mx, my + 30)], fill=(255, 0, 0, 255), width=2)

    out = Image.alpha_composite(img, grid).convert('RGB')
    out_path = a.out or os.path.splitext(a.input)[0] + '_grid.png'
    out.save(out_path)
    print(f'OK {w}x{h} -> {out_path}')


if __name__ == '__main__':
    main()
