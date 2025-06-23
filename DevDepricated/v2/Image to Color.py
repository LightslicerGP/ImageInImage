import os
from PIL import Image
import json

def get_average_color(folder_path, allow_transparency):
    color_dict = {}
    for file_name in os.listdir(folder_path):
        # Only process image files
        if not file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue
        with Image.open(os.path.join(folder_path, file_name)) as img:
            color = img.convert('RGBA').resize((1, 1)).getpixel((0, 0))
            hex_color = '#{0:02x}{1:02x}{2:02x}{3:02x}'.format(*color)

            green = '\033[32m'
            red = '\033[31m'
            reset = '\033[0m'
            if hex_color.endswith('ff', 7, 9):
                print(hex_color)
                print( green, 'Solid Color', reset)
                hex_color = '#{0:02x}{1:02x}{2:02x}'.format(*color)
                file_path = os.path.join(folder_path, file_name)
                color_dict[hex_color] = file_path
            elif not hex_color.endswith('ff', 7, 9) and not allow_transparency:
                print(hex_color)
                print(red, 'Unsolid Color', reset)
                continue
            elif not hex_color.endswith('ff', 7, 9) and allow_transparency:
                print(hex_color)
                print(red, 'Unsolid Color', reset)
                hex_color = '#{0:02x}{1:02x}{2:02x}'.format(*color)
                file_path = os.path.join(folder_path, file_name)
                color_dict[hex_color] = file_path
    with open('average_colors.json', 'w') as f:
        json.dump(color_dict, f, indent=4)
    for color, file_path in color_dict.items():
        print('{}: {}'.format(color, file_path))

get_average_color('Images', False)