import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageDraw, ImageTk
import random
import math
import time

class PoseGenerator:
    def __init__(self, root):
        self.root = root
        
        # Animation state
        self.animation_frame = 0
        self.is_animating = False
        
        # Pose presets with keyframes for animation
        self.pose_presets = {
            "Idle": {
                "description": "A relaxed, natural standing pose with subtle breathing motion",
                "keyframes": [
                    # Frame 1 - Normal stance
                    [(0.5, 0.2), (0.5, 0.4), (0.4, 0.6), (0.6, 0.6), (0.35, 0.8), (0.65, 0.8)],
                    # Frame 2 - Slight breathing motion
                    [(0.5, 0.19), (0.5, 0.39), (0.4, 0.59), (0.6, 0.59), (0.35, 0.79), (0.65, 0.79)],
                    # Frame 3 - Return to normal
                    [(0.5, 0.2), (0.5, 0.4), (0.4, 0.6), (0.6, 0.6), (0.35, 0.8), (0.65, 0.8)]
                ]
            },
            "Walking": {
                "description": "A dynamic walking pose with natural arm and leg movement",
                "keyframes": [
                    # Frame 1 - Left step
                    [(0.5, 0.2), (0.5, 0.4), (0.45, 0.6), (0.55, 0.6), (0.4, 0.8), (0.6, 0.75)],
                    # Frame 2 - Mid-step
                    [(0.5, 0.2), (0.5, 0.4), (0.4, 0.55), (0.6, 0.55), (0.45, 0.75), (0.55, 0.8)],
                    # Frame 3 - Right step
                    [(0.5, 0.2), (0.5, 0.4), (0.55, 0.6), (0.45, 0.6), (0.6, 0.75), (0.4, 0.8)]
                ]
            },
            "Running": {
                "description": "An energetic running pose with exaggerated limb movement",
                "keyframes": [
                    # Frame 1 - Push off
                    [(0.5, 0.2), (0.45, 0.35), (0.3, 0.5), (0.6, 0.3), (0.25, 0.6), (0.55, 0.45)],
                    # Frame 2 - Mid-air
                    [(0.5, 0.18), (0.45, 0.33), (0.25, 0.45), (0.65, 0.45), (0.3, 0.55), (0.6, 0.6)],
                    # Frame 3 - Landing
                    [(0.5, 0.2), (0.45, 0.35), (0.6, 0.5), (0.3, 0.3), (0.55, 0.6), (0.25, 0.45)]
                ]
            },
            "Jumping": {
                "description": "A dynamic jumping pose with anticipation and follow-through",
                "keyframes": [
                    # Frame 1 - Crouch
                    [(0.5, 0.25), (0.5, 0.45), (0.4, 0.6), (0.6, 0.6), (0.4, 0.8), (0.6, 0.8)],
                    # Frame 2 - Mid-air
                    [(0.5, 0.15), (0.5, 0.35), (0.35, 0.45), (0.65, 0.45), (0.4, 0.6), (0.6, 0.6)],
                    # Frame 3 - Landing
                    [(0.5, 0.25), (0.5, 0.45), (0.45, 0.65), (0.55, 0.65), (0.4, 0.8), (0.6, 0.8)]
                ]
            },
            "Action": {
                "description": "A dynamic action pose with strong diagonal lines",
                "keyframes": [
                    # Frame 1 - Wind-up
                    [(0.5, 0.2), (0.45, 0.35), (0.3, 0.4), (0.6, 0.45), (0.35, 0.6), (0.55, 0.7)],
                    # Frame 2 - Action moment
                    [(0.5, 0.2), (0.4, 0.35), (0.2, 0.45), (0.7, 0.4), (0.3, 0.65), (0.6, 0.7)],
                    # Frame 3 - Follow-through
                    [(0.5, 0.2), (0.45, 0.35), (0.35, 0.5), (0.65, 0.35), (0.4, 0.7), (0.5, 0.65)]
                ]
            },
            "Emotional": {
                "description": "An expressive pose showing strong emotion through body language",
                "keyframes": [
                    # Frame 1 - Build-up
                    [(0.5, 0.2), (0.5, 0.4), (0.4, 0.55), (0.6, 0.55), (0.45, 0.75), (0.55, 0.75)],
                    # Frame 2 - Emotional peak
                    [(0.5, 0.18), (0.5, 0.38), (0.35, 0.5), (0.65, 0.5), (0.4, 0.7), (0.6, 0.7)],
                    # Frame 3 - Release
                    [(0.5, 0.22), (0.5, 0.42), (0.45, 0.6), (0.55, 0.6), (0.5, 0.8), (0.5, 0.8)]
                ]
            },
            "Dance": {
                "description": "A flowing dance pose with graceful movement",
                "keyframes": [
                    # Frame 1 - First position
                    [(0.5, 0.2), (0.5, 0.4), (0.35, 0.5), (0.65, 0.5), (0.4, 0.7), (0.6, 0.7)],
                    # Frame 2 - Movement
                    [(0.5, 0.2), (0.45, 0.35), (0.3, 0.45), (0.7, 0.45), (0.35, 0.65), (0.65, 0.65)],
                    # Frame 3 - Final position
                    [(0.5, 0.2), (0.5, 0.4), (0.4, 0.55), (0.6, 0.55), (0.45, 0.75), (0.55, 0.75)]
                ]
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
            text="Advanced Pose Generator",
            font=("Helvetica", 24, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Controls frame
        controls_frame = tk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Pose selection
        pose_frame = tk.Frame(controls_frame)
        pose_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        pose_label = tk.Label(
            pose_frame,
            text="Select Pose:",
            font=("Helvetica", 12)
        )
        pose_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.pose_var = tk.StringVar()
        pose_dropdown = ttk.Combobox(
            pose_frame,
            textvariable=self.pose_var,
            values=list(self.pose_presets.keys()),
            state="readonly",
            width=30
        )
        pose_dropdown.pack(side=tk.LEFT)
        pose_dropdown.bind("<<ComboboxSelected>>", self.start_animation)
        
        # Canvas for pose visualization
        self.canvas = tk.Canvas(
            main_frame,
            width=600,
            height=400,
            bg="white",
            highlightthickness=1,
            highlightbackground="black"
        )
        self.canvas.pack(pady=20)
        
        # Pose description
        self.desc_var = tk.StringVar()
        self.desc_var.set("Select a pose to see its animation")
        desc_label = tk.Label(
            main_frame,
            textvariable=self.desc_var,
            font=("Helvetica", 12),
            wraplength=600
        )
        desc_label.pack(pady=10)
        
    def start_animation(self, event=None):
        pose_name = self.pose_var.get()
        if not pose_name:
            return
            
        self.current_pose = self.pose_presets[pose_name]
        self.animation_frame = 0
        self.is_animating = True
        self.animate()
        
        # Update description
        self.desc_var.set(self.current_pose["description"])
        
    def animate(self):
        if not self.is_animating:
            return
            
        # Create a new image
        width, height = 600, 400
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        
        # Get current keyframe
        keyframe = self.current_pose["keyframes"][self.animation_frame]
        
        # Draw the pose
        self.draw_pose(draw, width, height, keyframe)
        
        # Convert to PhotoImage and display
        self.photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
        # Update animation frame
        self.animation_frame = (self.animation_frame + 1) % len(self.current_pose["keyframes"])
        
        # Schedule next frame
        self.root.after(150, self.animate)
        
    def draw_pose(self, draw, width, height, joints):
        # Draw the character's body with smooth lines and better proportions
        
        # Head
        head_center = (int(joints[0][0] * width), int(joints[0][1] * height))
        head_radius = 20
        draw.ellipse([
            head_center[0] - head_radius,
            head_center[1] - head_radius,
            head_center[0] + head_radius,
            head_center[1] + head_radius
        ], outline="black", width=2)
        
        # Body (with slight curve for more natural look)
        body_start = head_center
        body_end = (int(joints[1][0] * width), int(joints[1][1] * height))
        self.draw_curved_line(draw, body_start, body_end, "black", 3)
        
        # Arms (with curves for more natural movement)
        arm_start = body_end
        left_arm_end = (int(joints[2][0] * width), int(joints[2][1] * height))
        right_arm_end = (int(joints[3][0] * width), int(joints[3][1] * height))
        self.draw_curved_line(draw, arm_start, left_arm_end, "black", 3)
        self.draw_curved_line(draw, arm_start, right_arm_end, "black", 3)
        
        # Legs (with curves for more natural movement)
        leg_start = body_end
        left_leg_end = (int(joints[4][0] * width), int(joints[4][1] * height))
        right_leg_end = (int(joints[5][0] * width), int(joints[5][1] * height))
        self.draw_curved_line(draw, leg_start, left_leg_end, "black", 3)
        self.draw_curved_line(draw, leg_start, right_leg_end, "black", 3)
        
        # Add joints for better visualization
        for joint in joints:
            x, y = int(joint[0] * width), int(joint[1] * height)
            draw.ellipse([x-4, y-4, x+4, y+4], fill="black")
            
    def draw_curved_line(self, draw, start, end, color, width):
        """Draw a curved line between two points for more natural movement"""
        # Calculate control point for quadratic curve
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        
        # Add slight curve based on line orientation
        curve_amount = 15
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        
        control_x = mid_x - dy / 4
        control_y = mid_y + dx / 4
        
        # Draw the curve using multiple small line segments
        points = []
        steps = 10
        for i in range(steps + 1):
            t = i / steps
            # Quadratic Bezier curve
            x = (1-t)**2 * start[0] + 2*(1-t)*t * control_x + t**2 * end[0]
            y = (1-t)**2 * start[1] + 2*(1-t)*t * control_y + t**2 * end[1]
            points.append((int(x), int(y)))
            
        for i in range(len(points) - 1):
            draw.line([points[i], points[i+1]], fill=color, width=width)

if __name__ == "__main__":
    root = tk.Tk()
    app = PoseGenerator(root)
    root.mainloop() 