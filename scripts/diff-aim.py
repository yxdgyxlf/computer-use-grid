# -*- coding: utf-8 -*-
"""diff-aim.py — 点击前校验环：双帧精确比对（v1）

用两张截图（P1=网格/基准帧，P2=光标显化帧）做像素 diff，
输出差异质心与目标位置的偏差，供"对准即点击"判定。

用法:
  python3 diff-aim.py P1.png P2.png --target X Y [--threshold 8] [--zoom box]
  --target X Y  目标位置（截图像素坐标）
  --threshold   对准阈值 px（默认 8；质心与目标距离 ≤ 阈值 → 对准）
  --zoom x1 y1 x2 y2  只看指定区域（默认全图；建议给目标附近 120x120 减少噪声）

输出:
  AIM_OK 或 AIM_MISS，含偏差与修正建议（delta = 目标 - 质心）
"""
import argparse
import numpy as np
from PIL import Image, ImageChops

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('p1')
    ap.add_argument('p2')
    ap.add_argument('--target', nargs=2, type=int, metavar=('X', 'Y'), required=True)
    ap.add_argument('--threshold', type=int, default=8)
    ap.add_argument('--zoom', nargs=4, type=int, metavar=('X1', 'Y1', 'X2', 'Y2'))
    a = ap.parse_args()

    im1 = Image.open(a.p1).convert('RGB')
    im2 = Image.open(a.p2).convert('RGB')
    assert im1.size == im2.size, f'size mismatch: {im1.size} vs {im2.size}'
    if a.zoom:
        im1 = im1.crop(a.zoom)
        im2 = im2.crop(a.zoom)
        tx, ty = a.target[0] - a.zoom[0], a.target[1] - a.zoom[1]
    else:
        tx, ty = a.target

    diff = ImageChops.difference(im1, im2)
    arr = np.array(diff)
    mask = arr.sum(axis=2) > 12
    n = int(mask.sum())
    if n == 0:
        print('AIM_UNKNOWN: no pixel change between frames (cursor hidden or not rendered)')
        return
    ys, xs = np.where(mask)
    cx, cy = float(xs.mean()), float(ys.mean())
    dist = ((cx - tx) ** 2 + (cy - ty) ** 2) ** 0.5
    status = 'AIM_OK' if dist <= a.threshold else 'AIM_MISS'
    dx, dy = tx - cx, ty - cy
    print(f'{status} diff_px={n} centroid=({cx:.1f},{cy:.1f}) target=({tx},{ty}) '
          f'dist={dist:.1f}px delta=({dx:+.1f},{dy:+.1f}) threshold={a.threshold}')
    if status == 'AIM_MISS':
        print(f'FIX: shift click coords by ({dx:+.0f},{dy:+.0f})px (screenshot space) and re-verify')

if __name__ == '__main__':
    main()
