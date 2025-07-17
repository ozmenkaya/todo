#!/usr/bin/env python3
"""
PWA ikon generator - SVG'den farklı boyutlarda PNG ikonları oluşturur
"""

import os
from PIL import Image, ImageDraw, ImageFont
import json

# İkon boyutları
ICON_SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

def create_icon(size):
    """Verilen boyutta bir ikon oluşturur"""
    # Yeni bir resim oluştur
    img = Image.new('RGBA', (size, size), (13, 110, 253, 255))  # Bootstrap primary color
    draw = ImageDraw.Draw(img)
    
    # Köşeleri yuvarla
    radius = size // 6
    
    # Yeni resim oluştur (rounded corners için)
    rounded_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    rounded_draw = ImageDraw.Draw(rounded_img)
    
    # Rounded rectangle çiz
    rounded_draw.rounded_rectangle([(0, 0), (size-1, size-1)], radius=radius, fill=(13, 110, 253, 255))
    
    # Text ekle
    try:
        # Font boyutunu resim boyutuna göre ayarla
        font_size = size // 4
        font = ImageFont.truetype("Arial.ttf", font_size)
    except:
        try:
            font = ImageFont.load_default()
        except:
            font = None
    
    # HX text'ini ortala
    text = "HX"
    if font:
        bbox = rounded_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    else:
        text_width = size // 3
        text_height = size // 6
    
    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2 - size // 12
    
    rounded_draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)
    
    # Alt text ekle
    sub_text = "TASKS"
    if font:
        try:
            sub_font = ImageFont.truetype("Arial.ttf", font_size // 4)
        except:
            sub_font = font
        
        bbox = rounded_draw.textbbox((0, 0), sub_text, font=sub_font)
        sub_text_width = bbox[2] - bbox[0]
        sub_text_x = (size - sub_text_width) // 2
        sub_text_y = text_y + text_height + size // 20
        
        rounded_draw.text((sub_text_x, sub_text_y), sub_text, fill=(255, 255, 255, 200), font=sub_font)
    
    return rounded_img

def generate_icons():
    """Tüm PWA ikonlarını oluşturur"""
    icons_dir = '/Users/ozmenkaya/todo/static/icons'
    
    # İkonları oluştur
    for size in ICON_SIZES:
        print(f"Creating icon {size}x{size}...")
        icon = create_icon(size)
        
        # PNG olarak kaydet
        icon_path = os.path.join(icons_dir, f'icon-{size}x{size}.png')
        icon.save(icon_path, 'PNG')
        print(f"Saved: {icon_path}")
    
    print("✅ All PWA icons created successfully!")

if __name__ == "__main__":
    generate_icons()
