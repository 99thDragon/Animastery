import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageDraw, ImageTk
import random
import math

class StyleSketcher:
    def __init__(self, root):
        self.root = root
        
        # Style presets
        self.style_presets = {
            "Fluid Motion, Soft Edges": {
                "colors": ["#4A90E2", "#357ABD", "#2C5F9E"],
                "shapes": "curves",
                "style": "soft"
            },
            "Bold Colors, High Contrast": {
                "colors": ["#FF0000", "#0000FF", "#FFFF00"],
                "shapes": "geometric",
                "style": "bold"
            },
            "Minimalist, Clean Lines": {
                "colors": ["#000000", "#FFFFFF"],
                "shapes": "basic",
                "style": "minimal"
            },
            "Organic, Natural Flow": {
                "colors": ["#2E8B57", "#3CB371", "#20B2AA"],
                "shapes": "organic",
                "style": "natural"
            },
            "Dynamic, Energetic": {
                "colors": ["#FF4500", "#FF8C00", "#FFD700"],
                "shapes": "dynamic",
                "style": "energetic"
            },
            "Soft, Dreamlike": {
                "colors": ["#FFB6C1", "#E6E6FA", "#DDA0DD"],
                "shapes": "soft",
                "style": "dreamy"
            },
            "Geometric, Structured": {
                "colors": ["#000000", "#808080", "#FFFFFF"],
                "shapes": "geometric",
                "style": "structured"
            }
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Style Sketcher AI",
            font=("Helvetica", 24, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Style selection
        style_frame = tk.Frame(main_frame)
        style_frame.pack(fill=tk.X, pady=(0, 20))
        
        style_label = tk.Label(
            style_frame,
            text="Select Style:",
            font=("Helvetica", 12)
        )
        style_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.style_var = tk.StringVar()
        style_dropdown = ttk.Combobox(
            style_frame,
            textvariable=self.style_var,
            values=list(self.style_presets.keys()),
            state="readonly",
            width=30
        )
        style_dropdown.pack(side=tk.LEFT)
        style_dropdown.bind("<<ComboboxSelected>>", self.generate_style)
        
        # Canvas for style visualization
        self.canvas = tk.Canvas(
            main_frame,
            width=600,
            height=400,
            bg="white",
            highlightthickness=1,
            highlightbackground="black"
        )
        self.canvas.pack(pady=20)
        
        # Style description
        self.desc_var = tk.StringVar()
        self.desc_var.set("Select a style to see its visualization")
        desc_label = tk.Label(
            main_frame,
            textvariable=self.desc_var,
            font=("Helvetica", 12),
            wraplength=600
        )
        desc_label.pack(pady=10)
        
    def generate_style(self, event=None):
        style_name = self.style_var.get()
        if not style_name:
            return
            
        preset = self.style_presets[style_name]
        
        # Create a new image
        width, height = 600, 400
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        
        # Generate style-specific visualization
        if preset["shapes"] == "curves":
            self.draw_curves(draw, width, height, preset["colors"])
        elif preset["shapes"] == "geometric":
            self.draw_geometric(draw, width, height, preset["colors"])
        elif preset["shapes"] == "basic":
            self.draw_basic(draw, width, height, preset["colors"])
        elif preset["shapes"] == "organic":
            self.draw_organic(draw, width, height, preset["colors"])
        elif preset["shapes"] == "dynamic":
            self.draw_dynamic(draw, width, height, preset["colors"])
        elif preset["shapes"] == "soft":
            self.draw_soft(draw, width, height, preset["colors"])
        elif preset["shapes"] == "structured":
            self.draw_structured(draw, width, height, preset["colors"])
        
        # Convert to PhotoImage and display
        self.photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
        # Update description
        self.update_description(style_name, preset)
        
    def draw_curves(self, draw, width, height, colors):
        for _ in range(10):
            color = random.choice(colors)
            points = []
            for i in range(5):
                x = random.randint(0, width)
                y = random.randint(0, height)
                points.append((x, y))
            draw.line(points, fill=color, width=3)
            
    def draw_geometric(self, draw, width, height, colors):
        for _ in range(8):
            color = random.choice(colors)
            x = random.randint(0, width-100)
            y = random.randint(0, height-100)
            size = random.randint(50, 100)
            if random.random() < 0.5:
                draw.rectangle([x, y, x+size, y+size], outline=color, width=3)
            else:
                draw.ellipse([x, y, x+size, y+size], outline=color, width=3)
            
    def draw_basic(self, draw, width, height, colors):
        for _ in range(5):
            color = random.choice(colors)
            x = random.randint(0, width-50)
            y = random.randint(0, height-50)
            size = random.randint(30, 50)
            draw.rectangle([x, y, x+size, y+size], outline=color, width=2)
            
    def draw_organic(self, draw, width, height, colors):
        for _ in range(15):
            color = random.choice(colors)
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(20, 40)
            draw.ellipse([x-size, y-size, x+size, y+size], outline=color, width=2)
            
    def draw_dynamic(self, draw, width, height, colors):
        for _ in range(12):
            color = random.choice(colors)
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = x1 + random.randint(-100, 100)
            y2 = y1 + random.randint(-100, 100)
            draw.line([(x1, y1), (x2, y2)], fill=color, width=3)
            
    def draw_soft(self, draw, width, height, colors):
        for _ in range(20):
            color = random.choice(colors)
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(10, 30)
            draw.ellipse([x-size, y-size, x+size, y+size], fill=color)
            
    def draw_structured(self, draw, width, height, colors):
        # Draw grid
        for i in range(0, width, 50):
            draw.line([(i, 0), (i, height)], fill=colors[0], width=1)
        for i in range(0, height, 50):
            draw.line([(0, i), (width, i)], fill=colors[0], width=1)
            
    def update_description(self, style_name, preset):
        descriptions = {
            "Fluid Motion, Soft Edges": "Flowing lines and soft transitions represent smooth character movements and gentle pose changes.",
            "Bold Colors, High Contrast": "Strong geometric shapes and vibrant colors create a dynamic, eye-catching style.",
            "Minimalist, Clean Lines": "Simple shapes and clean lines represent a modern, streamlined animation approach.",
            "Organic, Natural Flow": "Natural patterns and flowing forms suggest lifelike, fluid character movement.",
            "Dynamic, Energetic": "Sharp angles and warm colors convey energy and movement in character animation.",
            "Soft, Dreamlike": "Gentle gradients and blurred shapes create an ethereal, dreamy animation style.",
            "Geometric, Structured": "Precise lines and regular patterns represent a technical, structured animation approach."
        }
        self.desc_var.set(descriptions[style_name])

if __name__ == "__main__":
    root = tk.Tk()
    app = StyleSketcher(root)
    root.mainloop() 