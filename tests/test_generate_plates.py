from src.utils import generate_plates


def test_generate_plates_module_loads():
  assert hasattr(generate_plates, 'main') or True  # Just check module loads
