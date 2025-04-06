from PIL import Image, ImageDraw, ImageFont
import os

def create_logo():
    # Create a new image with a white background
    size = (200, 200)
    image = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw a circle
    circle_bbox = (20, 20, 180, 180)
    draw.ellipse(circle_bbox, fill="#FF6B6B")
    
    # Draw text
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
        
    text = "A"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    draw.text((x, y), text, font=font, fill="white")
    
    # Save the image
    image = image.resize((50, 50), Image.Resampling.LANCZOS)
    image.save("logo.png", "PNG")

if __name__ == "__main__":
    create_logo() 