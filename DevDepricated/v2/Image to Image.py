import json
import math
from PIL import Image
import os


def get_distance(color1, color2):
    r1, g1, b1 = color1
    r2, g2, b2, a2 = color2
    return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2 + a2)

def find_nearest_color(json_file, target_color):
    nearest_color = None
    nearest_distance = float('inf')
    nearest_file_path = None
    with open(json_file) as f:
        color_dict = json.load(f)
    for hex_color, file_path in color_dict.items():
        color_rgb = hex_to_rgb(hex_color)
        distance = get_distance(color_rgb, target_color)
        if distance < nearest_distance:
            nearest_color = color_rgb
            nearest_distance = distance
            nearest_file_path = file_path
    return nearest_color, nearest_file_path

def hex_to_rgb(hex_color):
    hex_value = hex_color.lstrip('#')
    if len(hex_value) == 6:
        color_tuple = tuple(int(hex_value[i:i+2], 16) for i in (0, 2, 4))
    elif len(hex_value) == 8:
        color_tuple = tuple(int(hex_value[i:i+2], 16) for i in (0, 2, 4, 8))
    return color_tuple

def image_creation(ref_image_path, ref_json_file, dest_folder):
    with Image.open(ref_image_path).convert('RGBA') as ref_image:
        width, height = ref_image.size
        final_dimensions = (width*16, height*16)
        final_image = Image.new('RGBA', final_dimensions)
        for x in range(width):
            for y in range(height): 
                color_rgb = ref_image.getpixel((x,y))[:4]
                pixel_opacity = ref_image.getpixel((x,y))[3]
                color_hex = '#' + bytes(color_rgb).hex()
                paste_image_path = find_nearest_color(ref_json_file, color_rgb)[1]
                with Image.open(paste_image_path) as paste_image:
                    if paste_image.size != (16, 16):
                        paste_image = paste_image.crop((0, 0, 16, 16))
                    if not pixel_opacity == 255:
                        paste_image.putalpha(pixel_opacity)
                    final_image.paste(paste_image, (x*16, y*16))
                print(f"Pixel at ({x},{y}) has color {color_hex}")
        final_image.save(os.path.join(dest_folder, os.path.basename(ref_image_path)))

def convert(ref_json, ref_folder, current_file, dest_folder):
    if current_file.lower().endswith(('.png', '.jpg', '.jpeg')):
        ref_image_path = os.path.join(ref_folder, current_file)
        print(ref_image_path)
        image_creation(ref_image_path, ref_json, dest_folder)
        
directory_path = 'Edited'
for filename in os.listdir(directory_path):
    if os.path.isfile(os.path.join(directory_path, filename)):
        convert('average_colors.json', directory_path, filename, 'Final')