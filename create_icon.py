#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import os

def create_app_icon():
    sizes = [(16, 16), (32, 32), (64, 64), (128, 128), (256, 256), (512, 512), (1024, 1024)]
    
    img = Image.new('RGBA', (1024, 1024), (102, 126, 234, 255))
    draw = ImageDraw.Draw(img)
    
    draw.ellipse([256, 256, 768, 768], fill=(118, 75, 162, 255))
    
    try:
        font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 300)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 300)
        except:
            font = ImageFont.load_default()
    
    text = "账"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (1024 - text_width) // 2
    y = (1024 - text_height) // 2 - 50
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    
    img.save('icon.png', 'PNG')
    print("✅ 已创建 icon.png")
    
    if os.path.exists('icon.icns'):
        os.remove('icon.icns')
    
    os.system('sips -s format icns icon.png --out icon.icns')
    print("✅ 已创建 icon.icns")
    
    if os.path.exists('icon.ico'):
        os.remove('icon.ico')
    
    img_ico = img.resize((256, 256), Image.Resampling.LANCZOS)
    img_ico.save('icon.ico', 'ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("✅ 已创建 icon.ico")

if __name__ == '__main__':
    create_app_icon()
