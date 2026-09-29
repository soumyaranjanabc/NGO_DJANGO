import os
from PIL import Image, ImageDraw, ImageFont

os.makedirs('static/images/gallery', exist_ok=True)

def create_logo():
    # 200x200 Indian Gov NGO logo
    img = Image.new('RGBA', (200, 200), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Outer circle
    draw.ellipse([10, 10, 190, 190], fill=(255, 250, 240), outline=(0, 33, 71), width=4)
    # Inner gold circle
    draw.ellipse([20, 20, 180, 180], outline=(217, 119, 6), width=2)
    # Ashoka chakra blue center
    draw.ellipse([60, 60, 140, 140], outline=(0, 0, 128), width=3)
    draw.ellipse([85, 85, 115, 115], fill=(0, 0, 128))
    
    # Chakra spokes
    for i in range(12):
        import math
        angle = i * (math.pi / 6)
        x1 = 100 + 15 * math.cos(angle)
        y1 = 100 + 15 * math.sin(angle)
        x2 = 100 + 38 * math.cos(angle)
        y2 = 100 + 38 * math.sin(angle)
        draw.line([x1, y1, x2, y2], fill=(0, 0, 128), width=2)

    # Tricolor arc on top and bottom
    draw.arc([14, 14, 186, 186], start=200, end=340, fill=(255, 153, 51), width=5)
    draw.arc([14, 14, 186, 186], start=20, end=160, fill=(19, 136, 8), width=5)
    
    img.save('static/images/ngo-logo.png')
    print("Created static/images/ngo-logo.png")

def create_hero():
    # 1200x600 Hero field banner
    img = Image.new('RGB', (1200, 600), (11, 37, 69))
    draw = ImageDraw.Draw(img)
    
    # Decorative gradient bands
    for y in range(600):
        r = int(11 + (y / 600) * 20)
        g = int(37 + (y / 600) * 30)
        b = int(69 + (y / 600) * 40)
        draw.line([(0, y), (1200, y)], fill=(r, g, b))
    
    # Left Tiranga ribbon
    draw.rectangle([0, 0, 16, 200], fill=(255, 153, 51))
    draw.rectangle([0, 200, 16, 400], fill=(255, 255, 255))
    draw.rectangle([0, 400, 16, 600], fill=(19, 136, 8))
    
    # Geometric decorative grid
    for x in range(50, 1200, 60):
        draw.line([(x, 0), (x, 600)], fill=(255, 255, 255, 15), width=1)
    for y in range(50, 600, 60):
        draw.line([(0, y), (1200, y)], fill=(255, 255, 255, 15), width=1)

    # Large subtle Ashoka chakra in background
    draw.ellipse([800, 100, 1200, 500], outline=(255, 255, 255), width=4)
    draw.ellipse([950, 250, 1050, 350], outline=(255, 255, 255), width=3)
    
    # Notice box
    draw.rectangle([100, 180, 750, 420], fill=(0, 33, 71), outline=(217, 119, 6), width=3)
    draw.rectangle([120, 200, 380, 235], fill=(217, 119, 6))
    
    img.save('static/images/hero-ngo-banner.jpg', quality=90)
    print("Created static/images/hero-ngo-banner.jpg")

def create_stamp():
    # 200x200 Official Verification Stamp
    img = Image.new('RGBA', (200, 200), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Double circle stamp
    draw.ellipse([10, 10, 190, 190], outline=(180, 83, 9), width=3)
    draw.ellipse([20, 20, 180, 180], outline=(180, 83, 9), width=2)
    
    # Star accents
    draw.ellipse([90, 80, 110, 100], fill=(180, 83, 9))
    draw.line([50, 100, 150, 100], fill=(180, 83, 9), width=2)
    draw.line([60, 115, 140, 115], fill=(180, 83, 9), width=1)
    
    img.save('static/images/ngo-stamp.png')
    print("Created static/images/ngo-stamp.png")

def create_gallery():
    colors = [
        ((30, 58, 138), (217, 119, 6), "Disaster Relief Operations"),
        ((22, 101, 52), (255, 255, 255), "Free Healthcare & Medical Camp"),
        ((124, 45, 18), (255, 153, 51), "Rural Literacy & Learning Drives"),
        ((6, 78, 59), (19, 136, 8), "Afforestation & River Restoration")
    ]
    for i, (bg, border, title) in enumerate(colors, 1):
        img = Image.new('RGB', (600, 400), bg)
        draw = ImageDraw.Draw(img)
        # Inner border
        draw.rectangle([15, 15, 585, 385], outline=border, width=2)
        # Central card
        draw.rectangle([80, 120, 520, 280], fill=(0, 20, 40), outline=(255, 255, 255), width=1)
        # Tricolor bottom bar
        draw.rectangle([80, 275, 226, 280], fill=(255, 153, 51))
        draw.rectangle([226, 275, 373, 280], fill=(255, 255, 255))
        draw.rectangle([373, 275, 520, 280], fill=(19, 136, 8))
        
        path = f'static/images/gallery/photo{i}.jpg'
        img.save(path, quality=85)
        print(f"Created {path}")

create_logo()
create_hero()
create_stamp()
create_gallery()
