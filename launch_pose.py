import tkinter as tk
from pose_generator import PoseGenerator

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Pose Generator")
    root.geometry("800x600")
    app = PoseGenerator(root)
    root.mainloop() 