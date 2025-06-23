import os
from PIL import Image
import json


def get_average_color(folder_path):
    # Iterates through all images in a folder and gets their average color
    color_dict = {}
    for file_name in os.listdir(folder_path):
        # Only process image files
        if not file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue
        # Open image and get average color
        with Image.open(os.path.join(folder_path, file_name)) as img:
            colors = img.convert('RGBA').getcolors(1)
            if colors is not None and len(colors) > 0:
                alpha = colors[0][1][3]
                if alpha < 255:
                    continue
            color = img.convert('RGB').resize((1, 1)).getpixel((0, 0))
            hex_color = '#{0:02x}{1:02x}{2:02x}'.format(*color)
            # Store the full path to the file in the dictionary
            file_path = os.path.join(folder_path, file_name)
            color_dict[hex_color] = file_path
    # Save color dictionary to a JSON file in the root directory of the project folder
    with open('average_colors.json', 'w') as f:
        json.dump(color_dict, f, indent=4)
    # Output filename and average color
    for color, file_path in color_dict.items():
        print('{}: {}'.format(color, file_path))


get_average_color('Images')