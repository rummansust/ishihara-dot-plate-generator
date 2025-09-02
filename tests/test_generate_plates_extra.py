import os
import random
from PIL import Image, ImageDraw
import numpy as np
import importlib

import src.utils.generate_plates as gp


def test_get_mask_areas(tmp_path):
  # create a small mask 32x32 with half pixels above threshold
  size = (32, 32)
  mask = Image.new('L', size)
  pixels = mask.load()
  threshold = gp.MASK_THRESHOLD
  total = size[0] * size[1]
  # set first half pixels >= threshold, rest < threshold
  count = 0
  for y in range(size[1]):
    for x in range(size[0]):
      if count < total // 2:
        pixels[x, y] = threshold + 10
      else:
        pixels[x, y] = threshold - 10
      count += 1
  p = tmp_path / "mask.png"
  mask.save(p)
  char_area, bg_area, total_area = gp.get_mask_areas(str(p), threshold=threshold)
  assert total_area == total
  assert char_area == total // 2
  assert bg_area == total - char_area


def test_draw_dots_inside_and_background(tmp_path, monkeypatch):
  # Use a larger IMG_SIZE so radii generation produces valid ranges
  orig_img_size = gp.IMG_SIZE
  gp.IMG_SIZE = (512, 512)
  try:
    random.seed(42)
    size = gp.IMG_SIZE
    # create a mask where entire image is character (value 255)
    mask = Image.new('L', size, color=255)
    draw_img = Image.new('RGB', size, (255, 255, 255))
    draw = ImageDraw.Draw(draw_img)
    colors_inside = [(10, 20, 30), (40, 50, 60)]
    colors_bg = [(200, 200, 200), (220, 220, 220)]
    total_area = size[0] * size[1]
    char_area = total_area

    # Test inside drawing
    dots, coverage, count = gp.draw_dots_inside_character(
        draw, mask, colors_inside, char_area,
        coverage_target=0.02, max_dots=200, timeout=1, verbose=False
    )
    assert isinstance(dots, list)
    assert count == len(dots)
    assert 0.0 <= coverage <= 1.0
    # Check that dot coords are inside bounds and colors chosen from list
    for x, y, r, c in dots:
      assert 0 <= x < gp.IMG_SIZE[0]
      assert 0 <= y < gp.IMG_SIZE[1]
      assert c in colors_inside

    # Test background drawing: create a mask where entire image is background (value 0)
    mask_bg = Image.new('L', size, color=0)
    # pass existing_dots from inside to avoid overlap
    bg_coverage, bg_count = gp.draw_dots_background(
        draw, mask_bg, colors_bg, bg_area=total_area,
        existing_dots=dots, coverage_target=0.02, max_dots=200, timeout=1, verbose=False
    )
    assert 0.0 <= bg_coverage <= 1.0
    assert isinstance(bg_count, int)
  finally:
    gp.IMG_SIZE = orig_img_size
