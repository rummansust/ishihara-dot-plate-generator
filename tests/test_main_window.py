import pytest
import tkinter as tk
from src.app.gui.main_window import PlateGameApp


# Ensure tests won't try to open a real X display in CI by using a hidden Tk subclass
class HiddenTk(tk.Tk):
  def __init__(self, *a, **kw):
    super().__init__(*a, **kw)
    try:
      self.withdraw()
    except Exception:
      pass


def test_app_initializes(monkeypatch):
  # Patch build_image_pool to avoid file IO
  monkeypatch.setattr('app.utils.image_pool.build_image_pool', lambda: [
      {'char': 'A', 'path': 'dummyA.png'},
      {'char': 'B', 'path': 'dummyB.png'}
  ])
  root = tk.Tk()
  # Don't show the GUI during unit tests
  root.withdraw()
  app = PlateGameApp(root)
  assert app.session is not None
  assert app.root is root
  assert hasattr(app, 'score_label')
  root.destroy()
