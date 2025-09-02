from src.app.utils.image_pool import build_image_pool


def test_build_image_pool():
  pool = build_image_pool()
  assert isinstance(pool, list)
  assert all('char' in img and 'path' in img for img in pool)
  assert len(pool) > 0
