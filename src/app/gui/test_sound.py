from playsound import playsound
import os

sound_path = os.path.join(os.path.dirname(__file__), '../../resources/correct.mp3')
print('Playing:', os.path.abspath(sound_path))
playsound(sound_path)
