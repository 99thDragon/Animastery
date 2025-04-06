import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import glob

class SpriteViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Sprite Animation Viewer")
        self.root.geometry("800x600")
        
        # Animation state
        self.current_frame = 0
        self.animation_speed = 150  # milliseconds between frames
        self.is_playing = False
        self.current_character = "aaron"
        self.current_animation = "idle"
        
        self.setup_ui()
        self.load_sprites()
        
    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Character Sprite Viewer",
            font=("Helvetica", 24, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Controls frame
        controls_frame = tk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Character selection
        char_frame = tk.Frame(controls_frame)
        char_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        char_label = tk.Label(
            char_frame,
            text="Character:",
            font=("Helvetica", 12)
        )
        char_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.char_var = tk.StringVar(value="aaron")
        char_dropdown = ttk.Combobox(
            char_frame,
            textvariable=self.char_var,
            values=["aaron", "mani"],
            state="readonly",
            width=15
        )
        char_dropdown.pack(side=tk.LEFT)
        char_dropdown.bind("<<ComboboxSelected>>", self.change_character)
        
        # Animation selection
        anim_frame = tk.Frame(controls_frame)
        anim_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        anim_label = tk.Label(
            anim_frame,
            text="Animation:",
            font=("Helvetica", 12)
        )
        anim_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.anim_var = tk.StringVar(value="idle")
        anim_dropdown = ttk.Combobox(
            anim_frame,
            textvariable=self.anim_var,
            values=["idle", "attack"],
            state="readonly",
            width=15
        )
        anim_dropdown.pack(side=tk.LEFT)
        anim_dropdown.bind("<<ComboboxSelected>>", self.change_animation)
        
        # Play/Pause button
        self.play_button = ttk.Button(
            controls_frame,
            text="Play",
            command=self.toggle_play
        )
        self.play_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Canvas for sprite display
        self.canvas = tk.Canvas(
            main_frame,
            width=400,
            height=400,
            bg="lightgray",
            highlightthickness=1,
            highlightbackground="black"
        )
        self.canvas.pack(pady=20)
        
    def load_sprites(self):
        self.sprites = {}
        for character in ["aaron", "mani"]:
            self.sprites[character] = {
                "idle": [],
                "attack": []
            }
            
            # Load idle animations
            idle_files = sorted(glob.glob(f"sprites/animations/{character}_idle_*.png"))
            for file in idle_files:
                image = Image.open(file)
                photo = ImageTk.PhotoImage(image)
                self.sprites[character]["idle"].append(photo)
            
            # Load attack animations
            attack_files = sorted(glob.glob(f"sprites/animations/{character}_attack_*.png"))
            for file in attack_files:
                image = Image.open(file)
                photo = ImageTk.PhotoImage(image)
                self.sprites[character]["attack"].append(photo)
        
        # Display first frame
        self.display_frame()
        
    def display_frame(self):
        current_sprites = self.sprites[self.current_character][self.current_animation]
        if current_sprites:
            # Clear canvas
            self.canvas.delete("all")
            
            # Get canvas dimensions
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Display sprite centered
            sprite = current_sprites[self.current_frame]
            x = (canvas_width - sprite.width()) // 2
            y = (canvas_height - sprite.height()) // 2
            self.canvas.create_image(x, y, anchor=tk.NW, image=sprite)
            
    def animate(self):
        if not self.is_playing:
            return
            
        current_sprites = self.sprites[self.current_character][self.current_animation]
        if current_sprites:
            self.current_frame = (self.current_frame + 1) % len(current_sprites)
            self.display_frame()
            self.root.after(self.animation_speed, self.animate)
            
    def toggle_play(self):
        self.is_playing = not self.is_playing
        self.play_button.config(text="Pause" if self.is_playing else "Play")
        if self.is_playing:
            self.animate()
            
    def change_character(self, event=None):
        self.current_character = self.char_var.get()
        self.current_frame = 0
        self.display_frame()
        
    def change_animation(self, event=None):
        self.current_animation = self.anim_var.get()
        self.current_frame = 0
        self.display_frame()

if __name__ == "__main__":
    root = tk.Tk()
    app = SpriteViewer(root)
    root.mainloop() 