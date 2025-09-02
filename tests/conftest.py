import tkinter as _tk
import pytest
import os
import sys

# Ensure the project root (one level up from tests/) is on sys.path so 'src' is importable.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
  sys.path.insert(0, ROOT)

# Hide Tk windows during tests by replacing tkinter.Tk with a wrapper that withdraws the root.


@pytest.fixture(autouse=True)
def _hide_tk_window(monkeypatch):
  """Automatically withdraw any created Tk root so GUI windows are not shown in CI."""
  original_tk = _tk.Tk

  class HiddenTk(original_tk):
    def __init__(self, *a, **kw):
      super().__init__(*a, **kw)
      try:
        self.withdraw()
      except Exception:
        pass

  monkeypatch.setattr(_tk, "Tk", HiddenTk)
  yield
