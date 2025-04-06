from PIL import Image, ImageDraw
import os
import math

def create_character_sprite(name, color, weapon_type):
    # Create a new image with a transparent background
    img = Image.new('RGBA', (300, 500), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Character colors
    body_color = color
    outline_color = (0, 0, 0)
    shadow_color = tuple(max(0, c - 50) for c in color)
    highlight_color = tuple(min(255, c + 50) for c in color)
    
    # Draw character body parts with more detail
    # Head with facial features and hair
    draw.ellipse([100, 50, 200, 150], fill=body_color, outline=outline_color)
    draw.ellipse([110, 60, 190, 140], fill=highlight_color, outline=outline_color)
    # Eyes with increased size and contrast
    draw.ellipse([120, 70, 150, 100], fill=(255, 255, 255), outline=outline_color)
    draw.ellipse([150, 70, 180, 100], fill=(255, 255, 255), outline=outline_color)
    draw.ellipse([130, 80, 140, 90], fill=(0, 0, 0))
    draw.ellipse([160, 80, 170, 90], fill=(0, 0, 0))
    # Mouth with increased contrast
    draw.arc([130, 110, 170, 130], start=0, end=180, fill=(0, 0, 0), width=3)
    # Hair
    draw.arc([100, 40, 200, 80], start=0, end=180, fill=outline_color, width=3)
    
    # Body with clothing details and patterns
    draw.rectangle([90, 150, 210, 350], fill=body_color, outline=outline_color)
    draw.rectangle([100, 160, 200, 340], fill=highlight_color, outline=outline_color)
    draw.line([90, 250, 210, 250], fill=outline_color, width=2)  # Belt
    draw.line([90, 300, 210, 300], fill=outline_color, width=2)  # Shirt pattern
    
    # Arms with muscles and accessories
    # Left arm
    draw.rectangle([50, 150, 90, 300], fill=body_color, outline=outline_color)
    draw.rectangle([60, 160, 80, 290], fill=highlight_color, outline=outline_color)
    # Right arm
    draw.rectangle([210, 150, 250, 300], fill=body_color, outline=outline_color)
    draw.rectangle([220, 160, 240, 290], fill=highlight_color, outline=outline_color)
    # Add wristbands with patterns
    draw.rectangle([50, 290, 90, 300], fill=(50, 50, 50), outline=outline_color)
    draw.line([50, 295, 90, 295], fill=highlight_color, width=1)
    draw.rectangle([210, 290, 250, 300], fill=(50, 50, 50), outline=outline_color)
    draw.line([210, 295, 250, 295], fill=highlight_color, width=1)
    
    # Legs with muscles and boots
    # Left leg
    draw.rectangle([90, 350, 140, 480], fill=body_color, outline=outline_color)
    draw.rectangle([100, 360, 130, 470], fill=highlight_color, outline=outline_color)
    # Right leg
    draw.rectangle([160, 350, 210, 480], fill=body_color, outline=outline_color)
    draw.rectangle([170, 360, 200, 470], fill=highlight_color, outline=outline_color)
    # Add boots with details
    draw.rectangle([90, 470, 140, 480], fill=(50, 50, 50), outline=outline_color)
    draw.line([90, 475, 140, 475], fill=highlight_color, width=1)
    draw.rectangle([160, 470, 210, 480], fill=(50, 50, 50), outline=outline_color)
    draw.line([160, 475, 210, 475], fill=highlight_color, width=1)
    
    # Draw weapon based on character type
    if weapon_type == "scythe":
        # Scythe blade with detail
        draw.polygon([(250, 200), (300, 150), (320, 200)], fill=(200, 0, 0), outline=outline_color)
        draw.polygon([(255, 195), (295, 155), (315, 195)], fill=(255, 0, 0), outline=outline_color)
        # Scythe handle with detail
        draw.rectangle([250, 200, 255, 300], fill=(100, 100, 100), outline=outline_color)
        draw.rectangle([251, 201, 254, 299], fill=(150, 150, 150), outline=outline_color)
        # Add scythe details and shading
        draw.line([(250, 200), (320, 200)], fill=(0, 0, 0), width=2)
        draw.line([(255, 205), (315, 205)], fill=highlight_color, width=1)
    elif weapon_type == "energy_blade":
        # Energy blade with glow effect
        draw.rectangle([250, 200, 280, 300], fill=(0, 0, 200), outline=outline_color)
        draw.rectangle([251, 201, 279, 299], fill=(0, 0, 255), outline=outline_color)
        # Energy effect with gradient
        for i in range(10):
            alpha = int(255 * (1 - i/10))
            draw.rectangle([280, 200+i*10, 285, 205+i*10], fill=(0, 100, 255, alpha), outline=outline_color)
        # Add energy blade details and glow
        draw.line([(250, 200), (280, 200)], fill=(0, 0, 0), width=2)
        draw.line([(255, 205), (275, 205)], fill=highlight_color, width=1)
    
    # Save the image
    if not os.path.exists('sprites'):
        os.makedirs('sprites')
    img.save(f'sprites/{name}_sprite.png')

def create_animation_frames(name, color, weapon_type, action):
    frames = []
    
    if action == "idle":
        # Create smoother breathing animation with more frames and secondary motion
        for i in range(32):
            img = Image.new('RGBA', (300, 500), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Define outline_color within the function
            outline_color = (0, 0, 0)
            
            # Calculate breathing offset
            breathing_offset = math.sin(i * math.pi / 16) * 3
            
            # Head with breathing motion
            draw.ellipse([100, 50+breathing_offset, 200, 150+breathing_offset], fill=color, outline=outline_color)
            draw.ellipse([110, 60+breathing_offset, 190, 140+breathing_offset], fill=tuple(min(255, c + 50) for c in color), outline=outline_color)
            
            # Body with breathing motion
            draw.rectangle([90, 150+breathing_offset, 210, 350+breathing_offset], fill=color, outline=outline_color)
            draw.rectangle([100, 160+breathing_offset, 200, 340+breathing_offset], fill=tuple(min(255, c + 50) for c in color), outline=outline_color)
            
            # Arms with slight movement
            arm_offset = math.sin(i * math.pi / 4) * 2
            draw.rectangle([50, 150+arm_offset, 90, 300+arm_offset], fill=color, outline=outline_color)
            draw.rectangle([60, 160+arm_offset, 80, 290+arm_offset], fill=tuple(min(255, c + 50) for c in color), outline=outline_color)
            draw.rectangle([210, 150+arm_offset, 250, 300+arm_offset], fill=color, outline=outline_color)
            draw.rectangle([220, 160+arm_offset, 240, 290+arm_offset], fill=tuple(min(255, c + 50) for c in color), outline=outline_color)
            
            # Legs
            draw.rectangle([90, 350, 140, 480], fill=color, outline=outline_color)
            draw.rectangle([100, 360, 130, 470], fill=tuple(min(255, c + 50) for c in color), outline=outline_color)
            draw.rectangle([160, 350, 210, 480], fill=color, outline=outline_color)
            draw.rectangle([170, 360, 200, 470], fill=tuple(min(255, c + 50) for c in color), outline=outline_color)
            
            # Add weapon with slight movement
            if weapon_type == "scythe":
                weapon_offset = math.sin(i * math.pi / 4) * 2
                draw.polygon([(250, 200+weapon_offset), (300, 150+weapon_offset), (320, 200+weapon_offset)], fill=(200, 0, 0), outline=(0, 0, 0))
                draw.polygon([(255, 195+weapon_offset), (295, 155+weapon_offset), (315, 195+weapon_offset)], fill=(255, 0, 0), outline=(0, 0, 0))
                draw.rectangle([250, 200+weapon_offset, 255, 300+weapon_offset], fill=(100, 100, 100), outline=(0, 0, 0))
                draw.rectangle([251, 201+weapon_offset, 254, 299+weapon_offset], fill=(150, 150, 150), outline=(0, 0, 0))
            elif weapon_type == "energy_blade":
                weapon_offset = math.sin(i * math.pi / 4) * 2
                draw.rectangle([250, 200+weapon_offset, 280, 300+weapon_offset], fill=(0, 0, 200), outline=(0, 0, 0))
                draw.rectangle([251, 201+weapon_offset, 279, 299+weapon_offset], fill=(0, 0, 255), outline=(0, 0, 0))
                for j in range(10):
                    alpha = int(255 * (1 - j/10))
                    draw.rectangle([280, 200+j*10+weapon_offset, 285, 205+j*10+weapon_offset], fill=(0, 100, 255, alpha), outline=(0, 0, 0))
            
            # Add secondary motion for hair
            hair_offset = math.sin(i * math.pi / 16) * 2
            draw.arc([100, 40+hair_offset, 200, 80+hair_offset], start=0, end=180, fill=outline_color, width=3)
            
            frames.append(img)
    
    elif action == "attack":
        # Create more dynamic attack animation with more frames and secondary motion
        for i in range(48):
            img = Image.new('RGBA', (300, 500), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Define outline_color within the function
            outline_color = (0, 0, 0)
            
            # Calculate attack motion
            attack_angle = i * 7.5  # Rotate for attack motion
            attack_offset = math.sin(i * math.pi / 24) * 20  # Forward motion
            
            # Head
            draw.ellipse([100, 50, 200, 150], fill=color, outline=(0, 0, 0))
            draw.ellipse([110, 60, 190, 140], fill=tuple(min(255, c + 50) for c in color), outline=(0, 0, 0))
            
            # Body with attack motion
            draw.rectangle([90, 150, 210, 350], fill=color, outline=(0, 0, 0))
            draw.rectangle([100, 160, 200, 340], fill=tuple(min(255, c + 50) for c in color), outline=(0, 0, 0))
            
            # Arms with attack motion
            arm_angle = attack_angle * 0.5
            arm_length = 100
            arm_x = 150 + math.cos(math.radians(arm_angle)) * arm_length
            arm_y = 200 + math.sin(math.radians(arm_angle)) * arm_length
            
            draw.rectangle([50, 150, 90, 300], fill=color, outline=(0, 0, 0))
            draw.rectangle([60, 160, 80, 290], fill=tuple(min(255, c + 50) for c in color), outline=(0, 0, 0))
            
            # Weapon with attack motion
            if weapon_type == "scythe":
                weapon_angle = attack_angle
                weapon_length = 150
                weapon_x = 200 + math.cos(math.radians(weapon_angle)) * weapon_length
                weapon_y = 200 + math.sin(math.radians(weapon_angle)) * weapon_length
                
                draw.polygon([(200, 200), (weapon_x, weapon_y-50), (weapon_x+20, weapon_y)], fill=(200, 0, 0), outline=(0, 0, 0))
                draw.polygon([(205, 195), (weapon_x-5, weapon_y-45), (weapon_x+15, weapon_y-5)], fill=(255, 0, 0), outline=(0, 0, 0))
                draw.rectangle([200, 200, 205, 300], fill=(100, 100, 100), outline=(0, 0, 0))
                draw.rectangle([201, 201, 204, 299], fill=(150, 150, 150), outline=(0, 0, 0))
            elif weapon_type == "energy_blade":
                # Calculate attack angle and length
                weapon_angle = attack_angle % 360
                weapon_length = 100
                
                # Base coordinates
                base_x, base_y = 200, 200
                
                # Calculate end point
                end_x = base_x + int(math.cos(math.radians(weapon_angle)) * weapon_length)
                end_y = base_y + int(math.sin(math.radians(weapon_angle)) * weapon_length)
                
                # Draw base energy blade
                points = [
                    (base_x, base_y),
                    (end_x, end_y),
                    (end_x + 10, end_y + 10),
                    (base_x + 10, base_y + 10)
                ]
                draw.polygon(points, fill=(0, 0, 200), outline=(0, 0, 0))
                
                # Add glow effect
                for i in range(5):
                    alpha = int(255 * (1 - i/5))
                    offset = i * 2
                    glow_points = [
                        (base_x - offset, base_y - offset),
                        (end_x - offset, end_y - offset),
                        (end_x + 10 + offset, end_y + 10 + offset),
                        (base_x + 10 + offset, base_y + 10 + offset)
                    ]
                    draw.polygon(glow_points, fill=(0, 100, 255, alpha))
                
                # Add energy particles
                for i in range(8):
                    particle_x = base_x + int(math.cos(math.radians(weapon_angle)) * (weapon_length * i / 8))
                    particle_y = base_y + int(math.sin(math.radians(weapon_angle)) * (weapon_length * i / 8))
                    particle_size = 6 - i
                    
                    # Ensure proper coordinate ordering for particles
                    x0 = particle_x
                    y0 = particle_y
                    x1 = particle_x + particle_size
                    y1 = particle_y + particle_size
                    
                    # Swap if needed
                    if x1 < x0:
                        x0, x1 = x1, x0
                    if y1 < y0:
                        y0, y1 = y1, y0
                        
                    draw.ellipse([x0, y0, x1, y1], fill=(0, 150, 255, 128))
            
            # Legs with attack stance
            leg_offset = math.sin(i * math.pi / 6) * 10
            draw.rectangle([90, 350, 140, 480], fill=color, outline=(0, 0, 0))
            draw.rectangle([100, 360, 130, 470], fill=tuple(min(255, c + 50) for c in color), outline=(0, 0, 0))
            draw.rectangle([160, 350+leg_offset, 210, 480+leg_offset], fill=color, outline=(0, 0, 0))
            draw.rectangle([170, 360+leg_offset, 200, 470+leg_offset], fill=tuple(min(255, c + 50) for c in color), outline=(0, 0, 0))
            
            # Add secondary motion for hair
            hair_offset = math.sin(i * math.pi / 24) * 2
            draw.arc([100, 40+hair_offset, 200, 80+hair_offset], start=0, end=180, fill=outline_color, width=3)
            
            frames.append(img)
    
    # Save animation frames
    if not os.path.exists('sprites/animations'):
        os.makedirs('sprites/animations')
    
    for i, frame in enumerate(frames):
        frame.save(f'sprites/animations/{name}_{action}_{i}.png')

# Create sprites for Aaron and Mani
create_character_sprite("aaron", (200, 0, 0), "scythe")  # Red color for Aaron
create_character_sprite("mani", (0, 0, 200), "energy_blade")  # Blue color for Mani

# Create animation frames
create_animation_frames("aaron", (200, 0, 0), "scythe", "idle")
create_animation_frames("aaron", (200, 0, 0), "scythe", "attack")
create_animation_frames("mani", (0, 0, 200), "energy_blade", "idle")
create_animation_frames("mani", (0, 0, 200), "energy_blade", "attack") 