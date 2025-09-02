import pytest
import tkinter as tk
from src.app.gui.main_window import PlateGameApp


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
