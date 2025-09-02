import os
import sys

# Ensure the project root (one level up from tests/) is on sys.path so 'src' is importable.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
  sys.path.insert(0, ROOT)
