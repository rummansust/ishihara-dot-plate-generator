import os
import json
from typing import List, Dict

PLATES_DIR = os.path.join(os.path.dirname(__file__), '../../plates')


def build_image_pool() -> List[Dict]:
  pool = []
  for char in os.listdir(PLATES_DIR):
    char_dir = os.path.join(PLATES_DIR, char)
    if not os.path.isdir(char_dir):
      continue
    for palette in os.listdir(char_dir):
      palette_dir = os.path.join(char_dir, palette)
      if not os.path.isdir(palette_dir):
        continue
      for fname in os.listdir(palette_dir):
        if fname.endswith('.png'):
          pool.append({
              'char': char,
              'palette': palette,
              'filename': fname,
              'path': os.path.join(palette_dir, fname)
          })
  return pool
