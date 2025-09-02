import pytest
from src.app.core.session import GameSession


def test_game_session_basic():
  pool = [
      {'char': 'A', 'path': 'dummyA.png'},
      {'char': 'B', 'path': 'dummyB.png'},
      {'char': 'C', 'path': 'dummyC.png'}
  ]
  session = GameSession(pool, num_images=2)
  session.start_new()
  assert session.current_index == 0
  assert session.score == 0
  assert len(session.selected_images) == 2
  # Simulate correct answer
  correct_char = session.selected_images[0]['char']
  is_correct, _ = session.answer(correct_char)
  assert is_correct
  assert session.score == 1
  # Simulate wrong answer
  is_correct, correct = session.answer('Z')
  assert not is_correct
  assert session.current_index == 2
  assert session.is_finished()
  assert session.get_score() == (1, 2)
