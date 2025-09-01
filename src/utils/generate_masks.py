import os
from PIL import Image, ImageDraw, ImageFont

MASKS_DIR = os.path.join(os.path.dirname(__file__), '../masks')
FONT_PATH = "/Library/Fonts/Comic Sans MS.ttf"  # Update if needed for your OS
IMG_SIZE = (64, 64)
FONT_SIZE = 48
CHARS = [str(i) for i in range(1, 11)] + [chr(i) for i in range(ord('A'), ord('Z')+1)]


def ensure_masks_dir():
  os.makedirs(MASKS_DIR, exist_ok=True)


def generate_mask(char):
  img = Image.new("L", IMG_SIZE, 0)
  draw = ImageDraw.Draw(img)
  try:
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
  except IOError:
    raise RuntimeError(f"Comic Sans font not found at {FONT_PATH}. Please update FONT_PATH.")
  w, h = draw.textsize(char, font=font)
  pos = ((IMG_SIZE[0] - w) // 2, (IMG_SIZE[1] - h) // 2)
  draw.text(pos, char, fill=255, font=font)
  # Binarize: 255 (white) for shape, 0 (black) for background
  bw = img.point(lambda x: 255 if x > 128 else 0, mode='1')
  bw.save(os.path.join(MASKS_DIR, f"{char}.png"))


def main():
  ensure_masks_dir()
  for char in CHARS:
    generate_mask(char)
  print(f"Masks generated in '{MASKS_DIR}' directory.")


if __name__ == "__main__":
  main()
