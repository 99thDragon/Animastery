import tkinter as tk
from tkinter import ttk
from style_sketcher import StyleSketcher
from pose_generator import PoseGenerator

class AnimationMaster:
    def __init__(self, root):
        self.root = root
        self.root.title("Animation Master")
        self.root.geometry("1200x600")
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create frames for each component
        self.style_frame = ttk.Frame(self.notebook)
        self.pose_frame = ttk.Frame(self.notebook)
        
        # Add tabs
        self.notebook.add(self.style_frame, text="Style Sketcher")
        self.notebook.add(self.pose_frame, text="Pose Generator")
        
        # Initialize components
        self.style_sketcher = StyleSketcher(self.style_frame)
        self.pose_generator = PoseGenerator(self.pose_frame)
        
        # Pack components
        self.style_sketcher.root.pack(fill=tk.BOTH, expand=True)
        self.pose_generator.root.pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = AnimationMaster(root)
    root.mainloop() 