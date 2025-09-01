import os
import json
import random
from typing import List, Dict

SESSION_FILE = os.path.join(os.path.dirname(__file__), '../resources/session.json')


class GameSession:
  def __init__(self, image_pool: List[Dict], num_images: int = 10):
    self.image_pool = image_pool
    self.num_images = num_images
    self.selected_images = []
    self.current_index = 0
    self.score = 0
    self.answered = []
    self.finished = False

  def start_new(self):
    pool = self.image_pool.copy()
    random.shuffle(pool)
    chars = list(set(img['char'] for img in pool))
    per_char = max(1, self.num_images // len(chars))
    selected = []
    for c in chars:
      char_imgs = [img for img in pool if img['char'] == c]
      random.shuffle(char_imgs)
      selected.extend(char_imgs[:per_char])
    while len(selected) < self.num_images:
      selected.append(random.choice(pool))
    random.shuffle(selected)
    self.selected_images = selected[:self.num_images]
    self.current_index = 0
    self.score = 0
    self.answered = []
    self.finished = False
    self.save()

  def save(self):
    data = {
        'selected_images': self.selected_images,
        'current_index': self.current_index,
        'score': self.score,
        'answered': self.answered,
        'finished': self.finished
    }
    with open(SESSION_FILE, 'w') as f:
      json.dump(data, f)

  def load(self):
    if not os.path.exists(SESSION_FILE):
      return False
    with open(SESSION_FILE, 'r') as f:
      data = json.load(f)
    self.selected_images = data['selected_images']
    self.current_index = data['current_index']
    self.score = data['score']
    self.answered = data['answered']
    self.finished = data['finished']
    return True

  def delete(self):
    if os.path.exists(SESSION_FILE):
      os.remove(SESSION_FILE)

  def answer(self, user_input: str):
    correct = self.selected_images[self.current_index]['char']
    is_correct = (user_input.strip().upper() == correct.upper())
    self.answered.append({'input': user_input, 'correct': correct, 'result': is_correct})
    if is_correct:
      self.score += 1
    self.current_index += 1
    if self.current_index >= len(self.selected_images):
      self.finished = True
    self.save()
    return is_correct, correct

  def skip(self):
    self.answered.append(
        {'input': '', 'correct': self.selected_images[self.current_index]['char'], 'result': False, 'skipped': True})
    self.current_index += 1
    if self.current_index >= len(self.selected_images):
      self.finished = True
    self.save()

  def get_current_image(self):
    if self.current_index < len(self.selected_images):
      return self.selected_images[self.current_index]
    return None

  def get_score(self):
    return self.score, len(self.selected_images)

  def is_finished(self):
    return self.finished
