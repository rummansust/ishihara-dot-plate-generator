import os
import json
from PIL import Image
import src.utils.generate_plates as gp


def _write_dummy_mask(path, size=(32, 32)):
  img = Image.new('L', size, color=255)
  img.save(path)


class _ImmediateExecutor:
  def __init__(self, *args, **kwargs):
    self._futures = []

  def submit(self, fn, *args, **kwargs):
    # Execute immediately and return a dummy future with result
    class F:
      def __init__(self, fn, args, kwargs):
        self._fn = fn
        self._args = args
        self._kwargs = kwargs
        self._res = None

      def result(self):
        # Call function once and return
        self._res = self._fn(*self._args, **self._kwargs)
        return self._res

    f = F(fn, args, kwargs)
    return f

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc, tb):
    return False


def test_main_skips_when_cache_complete(tmp_path, capsys, monkeypatch):
  # Setup: one mask file
  masks_dir = tmp_path / "masks"
  masks_dir.mkdir()
  mask_path = masks_dir / "X.png"
  _write_dummy_mask(mask_path)

  # Create plates output that appears complete
  # Determine base plates dir as used by generate_plates.main
  base_dir = tmp_path / "plates_root"
  char_dir = base_dir / "X"
  palette_name = "Test Palette"
  safe_name = palette_name.replace(' ', '_')
  out_dir = char_dir / safe_name
  out_dir.mkdir(parents=True)
  # create run images and summary
  (out_dir / "run_1.png").write_text("img")
  summary = [{"image": "run_1.png"}]
  with open(out_dir / "summary.json", "w") as f:
    json.dump(summary, f)
  # create char level summary
  char_summary = [{"image": "run_1.png"}]
  with open(char_dir / "summary.json", "w") as f:
    json.dump(char_summary, f)

  # Monkeypatch module paths & palettes
  monkeypatch.setattr(gp, 'MASKS_DIR', str(masks_dir))
  monkeypatch.setattr(gp, 'palettes', [{'name': palette_name}])
  # Monkeypatch the __file__ dirname usage by making plates path resolve to our base_dir
  fake_dir = tmp_path / "fake_src" / "utils"
  fake_dir.mkdir(parents=True)
  # Set module __file__ to point inside fake_dir so out_dir resolves under tmp_path
  monkeypatch.setattr(gp, '__file__', str(fake_dir / 'generate_plates.py'))

  # But process main computes out_dir relative to os.path.dirname(__file__) + '../plates/{char}'
  # Therefore create that path under fake_dir's parent
  plates_parent = fake_dir.parent / 'plates'
  plates_parent.mkdir(parents=True, exist_ok=True)
  # move our pre-created char dir into this location
  dest_char_dir = plates_parent / 'X'
  dest_char_dir.parent.mkdir(parents=True, exist_ok=True)
  # copy structure from out_dir to dest_char_dir
  import shutil
  if dest_char_dir.exists():
    shutil.rmtree(dest_char_dir)
  shutil.copytree(char_dir, dest_char_dir)
  # Now run main()
  gp.main()
  captured = capsys.readouterr()
  assert "[CACHE] All outputs for character 'X' exist. Skipping generation." in captured.out


def test_main_regenerates_when_incomplete(tmp_path, monkeypatch):
  # Setup: one mask file
  masks_dir = tmp_path / "masks"
  masks_dir.mkdir()
  mask_path = masks_dir / "Y.png"
  _write_dummy_mask(mask_path)

  # Setup fake module dir to redirect plates output
  fake_dir = tmp_path / "fake_src" / "utils"
  fake_dir.mkdir(parents=True, exist_ok=True)
  monkeypatch.setattr(gp, '__file__', str(fake_dir / 'generate_plates.py'))
  monkeypatch.setattr(gp, 'MASKS_DIR', str(masks_dir))
  # Simple palette list
  monkeypatch.setattr(gp, 'palettes', [{'name': 'P'}])

  # Monkeypatch heavy drawing functions to be lightweight and deterministic
  monkeypatch.setattr(gp, 'draw_dots_inside_character', lambda *a, **k: ([], 0.0, 0))
  monkeypatch.setattr(gp, 'draw_dots_background', lambda *a, **k: (0.0, 0))
  # Replace ThreadPoolExecutor with immediate executor to avoid concurrency
  monkeypatch.setattr(gp, 'ThreadPoolExecutor', _ImmediateExecutor)
  # Make as_completed simply iterate over the provided futures (our immediate futures)
  monkeypatch.setattr(gp, 'as_completed', lambda futures: futures)

  # Ensure no existing char dir so main will generate
  plates_parent = fake_dir.parent / 'plates'
  if plates_parent.exists():
    import shutil
    shutil.rmtree(plates_parent)

  # Run main (should create plates and write summaries)
  gp.main()

  # Check that overall_summary.json exists under plates_parent
  overall = plates_parent / 'overall_summary.json'
  assert overall.exists()
  with open(overall) as f:
    data = json.load(f)
  assert 'characters' in data
  # There should be one character entry for 'Y'
  chars = [c['character'] for c in data['characters']]
  assert 'Y' in chars
