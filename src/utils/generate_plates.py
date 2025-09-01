import json
import os
import random
from PIL import Image, ImageDraw
import math
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np

# Update paths to be correct relative to utils/
with open(os.path.join(os.path.dirname(__file__), '../resources/color_palettes.json')) as f:
  palettes = json.load(f)["palettes"]

IMG_SIZE = (4048, 4048)
MASKS_DIR = os.path.join(os.path.dirname(__file__), '../masks')
MASK_THRESHOLD = 200


def get_mask_areas(mask_path, threshold=200):
  mask = Image.open(mask_path).convert('L')
  arr = np.array(mask)
  char_area = int(np.sum(arr >= threshold))
  bg_area = int(np.sum(arr < threshold))
  total_area = arr.size
  return char_area, bg_area, total_area


def draw_dots_inside_character(draw, mask, colors, char_area, coverage_target=0.60, max_dots=4000, timeout=4, verbose=True):
  radius_variants = int(42)
  base_radius = int(8)
  min_radius = int(base_radius * 2)
  max_radius = int(base_radius * 15)
  radii = list(range(min_radius, max_radius + 1, int((max_radius - min_radius) // radius_variants) or 1))
  n = len(radii)
  weights = [4] + [2]*(n-2) + [4] if n > 2 else [1]*n
  dots = []
  total_area = char_area
  drawn_area = 0.0
  start_time = time.time()
  mask_pixels = mask.load()
  while (drawn_area / total_area < coverage_target) and (len(dots) < max_dots) and (time.time() - start_time < timeout):
    radius = random.choices(radii, weights=weights, k=1)[0]
    x = random.randint(radius, IMG_SIZE[0] - radius)
    y = random.randint(radius, IMG_SIZE[1] - radius)
    if mask_pixels[x, y] < MASK_THRESHOLD:
      continue
    too_close = False
    for (ox, oy, orad, _) in dots:
      dist = ((x - ox)**2 + (y - oy)**2)**0.5
      if dist < radius + orad - 2:
        too_close = True
        break
    if not too_close:
      color = random.choice(colors)
      dots.append((x, y, radius, color))
      drawn_area += math.pi * (radius ** 2)
  for (x, y, radius, color) in dots:
    draw.ellipse([
        x - radius, y - radius,
        x + radius, y + radius
    ], fill=tuple(color))
  if verbose:
    print(
        f"[INSIDE] Target coverage: {coverage_target:.2%}, Estimated (sum of circles) coverage: {drawn_area / total_area:.2%}, Dots: {len(dots)}")
  return dots, drawn_area / total_area, len(dots)


def draw_dots_background(draw, mask, colors, bg_area, existing_dots, coverage_target=0.60, max_dots=4000, timeout=4, verbose=True):
  radius_variants = int(42)
  base_radius = int(8)
  min_radius = int(base_radius * 2)
  max_radius = int(base_radius * 15)
  radii = list(range(min_radius, max_radius + 1, int((max_radius - min_radius) // radius_variants) or 1))
  n = len(radii)
  weights = [4] + [2]*(n-2) + [4] if n > 2 else [1]*n
  dots = []
  total_area = bg_area
  drawn_area = 0.0
  start_time = time.time()
  mask_pixels = mask.load()
  all_dots = existing_dots.copy()
  while (drawn_area / total_area < coverage_target) and (len(dots) < max_dots) and (time.time() - start_time < timeout):
    radius = random.choices(radii, weights=weights, k=1)[0]
    x = random.randint(radius, IMG_SIZE[0] - radius)
    y = random.randint(radius, IMG_SIZE[1] - radius)
    if mask_pixels[x, y] >= MASK_THRESHOLD:
      continue
    too_close = False
    for (ox, oy, orad, _) in all_dots:
      dist = ((x - ox)**2 + (y - oy)**2)**0.5
      if dist < radius + orad - 2:
        too_close = True
        break
    if not too_close:
      color = random.choice(colors)
      dots.append((x, y, radius, color))
      all_dots.append((x, y, radius, color))
      drawn_area += math.pi * (radius ** 2)
  for (x, y, radius, color) in dots:
    draw.ellipse([
        x - radius, y - radius,
        x + radius, y + radius
    ], fill=tuple(color))
  if verbose:
    print(
        f"[BACKGROUND] Target coverage: {coverage_target:.2%}, Estimated (sum of circles) coverage: {drawn_area / total_area:.2%}, Dots: {len(dots)}")
  return drawn_area / total_area, len(dots)


def main():
  coverage_target = 0.60
  max_dots = 4000
  timeout = 4
  runs_per_target = 3
  overall_start = time.time()
  all_char_summaries = []
  mask_files = [f for f in os.listdir(MASKS_DIR) if f.endswith('.png')]
  for mask_file in mask_files:
    char = os.path.splitext(mask_file)[0]
    mask_path = os.path.join(MASKS_DIR, mask_file)
    char_dir = os.path.join(os.path.dirname(__file__), f'../plates/{char}')
    # --- CACHE LOGIC START ---
    skip_char = False
    if os.path.exists(char_dir):
      all_palettes_ok = True
      for palette in palettes:
        safe_name = palette['name'].replace(' ', '_').replace('/', '_').replace('\\', '_')
        out_dir = os.path.join(char_dir, safe_name)
        summary_path = os.path.join(out_dir, 'summary.json')
        # Check summary exists
        if not os.path.exists(summary_path):
          all_palettes_ok = False
          break
        # Check all images exist
        try:
          with open(summary_path) as f:
            summary = json.load(f)
          for entry in summary:
            img_path = os.path.join(out_dir, entry['image'])
            if not os.path.exists(img_path):
              all_palettes_ok = False
              break
        except Exception:
          all_palettes_ok = False
          break
        if not all_palettes_ok:
          break
      # Check per-character summary
      char_summary_path = os.path.join(char_dir, 'summary.json')
      if not os.path.exists(char_summary_path):
        all_palettes_ok = False
      if all_palettes_ok:
        print(f"[CACHE] All outputs for character '{char}' exist. Skipping generation.")
        skip_char = True
      else:
        print(f"[CACHE] Incomplete outputs for character '{char}'. Deleting and regenerating...")
        import shutil
        shutil.rmtree(char_dir)
    if skip_char:
      continue
    # --- CACHE LOGIC END ---
    char_area, bg_area, total_area = get_mask_areas(mask_path, MASK_THRESHOLD)
    mask = Image.open(mask_path).convert('L')
    char_palette_summaries = []

    def process_palette(palette):
      safe_name = palette['name'].replace(' ', '_').replace('/', '_').replace('\\', '_')
      out_dir = os.path.join(os.path.dirname(__file__), f'../plates/{char}/{safe_name}')
      os.makedirs(out_dir, exist_ok=True)
      summary = []
      print(
          f"[START] Generating plates for palette: {palette['name']} and mask: {char} at {time.strftime('%Y-%m-%d %H:%M:%S')}")
      for run_idx in range(1, runs_per_target + 1):
        img = Image.new("RGB", IMG_SIZE, (255, 255, 255))
        draw = ImageDraw.Draw(img)
        t0 = time.time()
        inside_colors = palette["figure"] if "figure" in palette else [(0, 0, 0)]
        bg_colors = palette["background"] if "background" in palette else [(255, 255, 255)]
        inside_dots, inside_coverage, inside_count = draw_dots_inside_character(
            draw, mask, inside_colors, char_area, coverage_target=coverage_target, max_dots=max_dots, timeout=timeout, verbose=True)
        bg_coverage, bg_count = draw_dots_background(
            draw, mask, bg_colors, bg_area, existing_dots=inside_dots, coverage_target=coverage_target, max_dots=max_dots, timeout=timeout, verbose=True)
        t1 = time.time()
        out_path = os.path.join(out_dir, f"run_{run_idx}.png")
        img.save(out_path)
        print(f"Saved {out_path} in {t1-t0:.2f}s")
        summary.append({
            "image": f"run_{run_idx}.png",
            "inside_coverage": inside_coverage,
            "inside_dot_count": inside_count,
            "background_coverage": bg_coverage,
            "background_dot_count": bg_count,
            "time_sec": round(t1-t0, 2)
        })
      print(f"[END] Finished palette: {palette['name']} and mask: {char} at {time.strftime('%Y-%m-%d %H:%M:%S')}")
      with open(os.path.join(out_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
      print(f"Summary written to {os.path.join(out_dir, 'summary.json')}")
      char_palette_summaries.append({
          "palette": palette['name'],
          "summary": summary
      })
    with ThreadPoolExecutor(max_workers=6) as executor:
      futures = [executor.submit(process_palette, palette) for palette in palettes]
      for future in as_completed(futures):
        future.result()
    # Save per-character summary
    char_summary = {
        "character": char,
        "character_area": char_area,
        "background_area": bg_area,
        "total_area": total_area,
        "palettes": char_palette_summaries
    }
    out_dir_char = os.path.join(os.path.dirname(__file__), f'../plates/{char}')
    os.makedirs(out_dir_char, exist_ok=True)
    with open(os.path.join(out_dir_char, 'summary.json'), 'w') as f:
      json.dump(char_summary, f, indent=2)
    all_char_summaries.append(char_summary)
  overall_end = time.time()
  # Save global summary
  global_summary = {
      "total_runtime_sec": round(overall_end - overall_start, 2),
      "characters": all_char_summaries
  }
  out_dir_main = os.path.join(os.path.dirname(__file__), '../plates')
  os.makedirs(out_dir_main, exist_ok=True)
  with open(os.path.join(out_dir_main, 'overall_summary.json'), 'w') as f:
    json.dump(global_summary, f, indent=2)
  print(f"Global summary written to {os.path.join(out_dir_main, 'overall_summary.json')}")


if __name__ == "__main__":
  main()
