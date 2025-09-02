from src.utils import generate_masks


def test_generate_mask_function_exists():
  assert hasattr(generate_masks, 'generate_mask')
