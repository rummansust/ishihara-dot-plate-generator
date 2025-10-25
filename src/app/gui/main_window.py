import os
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import customtkinter as ctk
from PIL import Image, ImageTk
from app.core.session import GameSession
from app.utils.image_pool import build_image_pool

# Sound support
import threading
try:
  from playsound import playsound
except ImportError:
  playsound = None


class PlateGameApp:
  def __init__(self, root):
    self.root = root
    self.root.title('Ishihara Plate Game')
    # Sound file paths (set early so show_image()/show_summary() can call play_sound)
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../resources'))
    self.sound_buzz = os.path.join(base, 'buzz.mp3')
    self.sound_correct = os.path.join(base, 'correct.mp3')
    self.sound_cheer = os.path.join(base, 'cheer.mp3')
    self.sound_trumpet = os.path.join(base, 'trumpet_fail.mp3')

    self.pool = build_image_pool()
    self.session = GameSession(self.pool)
    if not self.session.load():
      self.session.start_new()
    self.setup_ui()
    self.show_image()

    # Sound file paths
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../resources'))
    self.sound_buzz = os.path.join(base, 'buzz.mp3')
    self.sound_correct = os.path.join(base, 'correct.mp3')
    self.sound_cheer = os.path.join(base, 'cheer.mp3')
    self.sound_trumpet = os.path.join(base, 'trumpet_fail.mp3')

  def play_sound(self, path):
    if playsound and os.path.exists(path):
      threading.Thread(target=playsound, args=(path,), daemon=True).start()

  def setup_ui(self):
    self.root.geometry('1000x820')
    self.root.configure(bg='#e3f2fd')
    comic = ('Comic Sans MS', 22)
    comic_large = ('Comic Sans MS', 28, 'bold')
    comic_btn = ('Comic Sans MS', 20, 'bold')

    style = ttk.Style()
    style.theme_use('clam')
    # Entry style
    style.configure('Custom.TEntry',
                    fieldbackground='#bbdefb',
                    background='#bbdefb',
                    foreground='#263238',
                    borderwidth=0,
                    relief='flat',
                    padding=8,
                    font=comic_large)
    style.map('Custom.TEntry',
              fieldbackground=[('active', '#bbdefb'), ('!active', '#bbdefb'), ('focus', '#bbdefb')],
              foreground=[('active', '#263238'), ('!active', '#263238'), ('focus', '#263238')])
    # Button style
    style.configure('Green.TButton',
                    background='#43a047',
                    foreground='white',
                    font=comic_btn,
                    borderwidth=0,
                    focusthickness=3,
                    focuscolor='#388e3c',
                    padding=10)
    style.map('Green.TButton',
              background=[('active', '#388e3c')],
              relief=[('pressed', 'flat'), ('!pressed', 'flat')])

    # Score label
    self.score_label = ctk.CTkLabel(
        self.root,
        text='',
        font=('Comic Sans MS', 20, 'bold'),
        text_color='#1565c0',
        fg_color='#bbdefb',
        corner_radius=16,
        width=380,
        height=48
    )
    self.score_label.pack(pady=(18, 10))
    # Restart button
    restart_img_path = os.path.join(os.path.dirname(__file__), '../../resources/restart.png')
    restart_img = Image.open(restart_img_path)
    restart_img = restart_img.resize((44, 44), Image.LANCZOS)
    self.restart_photo = ctk.CTkImage(light_image=restart_img, dark_image=restart_img, size=(44, 44))
    self.restart_btn = ctk.CTkButton(
        self.root,
        text='',
        image=self.restart_photo,
        width=44,
        height=44,
        corner_radius=22,
        fg_color='#e3f2fd',
        hover_color="#e3f2fd",
        command=None  # Will set command later
    )
    self.restart_btn.place(x=18, y=18)
    self.restart_btn.place_forget()
    self.img_label = tk.Label(self.root, bg='#e3f2fd')
    self.img_label.pack(pady=(10, 10))
    self.entry = ctk.CTkEntry(
        self.root,
        font=comic_large,
        justify='center',
        fg_color='#bbdefb',
        text_color='#263238',
        border_width=0,
        corner_radius=16,
        width=320,
        height=60
    )
    self.entry.pack(pady=10, padx=60, fill='x')
    self.entry.bind('<Return>', lambda e: self.submit())
    self.feedback = tk.Label(self.root, text='', font=comic, fg='black', bg='#e3f2fd')
    self.feedback.pack(pady=10)
    btn_frame = tk.Frame(self.root, bg="#e3f2fd")
    btn_frame.pack(pady=2)
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")
    self.next_btn = ctk.CTkButton(
        btn_frame,
        text="Next",
        command=self.submit,
        font=comic_btn,
        fg_color="#43a047",
        text_color="white",
        hover_color="#388e3c",
        corner_radius=16,
        width=180,
        height=44
    )
    self.next_btn.pack(side="left", padx=10, pady=12)
    self.next_btn.configure(cursor="hand2")
    self.root.protocol('WM_DELETE_WINDOW', self.on_close)
    self.restart_btn.configure(command=self.restart_game)
    self.restart_btn.configure(command=self.restart_game)

  def show_image(self):
    img_info = self.session.get_current_image()
    if img_info is None:
      self.show_summary()
      return
    img = Image.open(img_info['path'])
    img = img.resize((400, 400))
    self.tk_img = ImageTk.PhotoImage(img)
    self.img_label.config(image=self.tk_img)
    self.entry.configure(state='normal')
    self.next_btn.configure(state='normal')
    self.entry.delete(0, tk.END)
    self.feedback.config(text='', fg='black')
    score, total = self.session.get_score()
    self.score_label.configure(text=f'Score: {score}/{total}   |   Plate {self.session.current_index+1} of {total}')

  def submit(self):
    user_input = self.entry.get()
    if not user_input:
      self.feedback.configure(text='❗ Please enter a character.', fg='orange', bg='#e3f2fd')
      self.feedback.lift()
      self.play_sound(self.sound_buzz)
      return
    self.entry.delete(0, tk.END)  # Clear entry immediately
    self.entry.configure(state='disabled')
    self.next_btn.configure(state='disabled')
    is_correct, correct = self.session.answer(user_input)
    if is_correct:
      self.play_sound(self.sound_correct)
      self.show_feedback('✅ Correct!', 'green')
    else:
      self.play_sound(self.sound_buzz)
      self.show_feedback(f'❌ Wrong! Correct: {correct}', 'red')

  def show_feedback(self, message, color):
    self.feedback.config(text=message, fg=color)
    self.feedback.lift()
    if self.session.is_finished():
      self.root.after(500, self.show_summary)
    else:
      self.root.after(500, self.show_image)

  def show_summary(self):
    score, total = self.session.get_score()
    if total > 0 and score / total < 0.5:
      msg = f'❌ Game Over!!!\t|\tScore: {score}/{total}\nKeep practicing!'
      color = '#e53935'  # vibrant red
      self.play_sound(self.sound_trumpet)
    else:
      msg = f'🎉 Game Over!!!\t|\tScore: {score}/{total}\nGreat job!'
      color = '#2ecc40'  # vibrant green
      self.play_sound(self.sound_cheer)
    # Update score label to show final score
    self.score_label.configure(text=f'Score: {score}/{total}   |   Plate {total} of {total}')
    # Show restart button at top left (always)
    self.restart_btn.place(x=18, y=18)
    # Disable input and next button
    self.entry.configure(state='disabled')
    self.next_btn.configure(state='disabled')
    # Show message in feedback area with appropriate color
    self.feedback.config(text=msg, fg=color, bg='#e3f2fd')

  def on_close(self):
    self.session.delete()
    self.root.destroy()

  def restart_game(self):
    self.session.delete()
    self.session.start_new()
    self.restart_btn.place_forget()
    self.feedback.config(text='', fg='black', bg='#e3f2fd')
    self.show_image()


def run_app():
  root = tk.Tk()
  app = PlateGameApp(root)
  root.mainloop()
