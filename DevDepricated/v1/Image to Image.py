import os
import numpy as np
import json
from PIL import Image

def map_pixels(color_file, input_folder, output_folder):
    with open(color_file) as f:
        color_map = json.load(f)
    
    for filename in os.listdir(input_folder):
        image_path = os.path.join(input_folder, filename)
        image = Image.open(image_path)
        pixels = np.array(image)
        height, width, _ = pixels.shape
        for i in range(height):
            for j in range(width):
                hex_color = '#{:02x}{:02x}{:02x}'.format(*pixels[i,j])
                closest_color = min(color_map.keys(), key=lambda c: abs(int(c, 16) - int(hex_color, 16)))
                pixels[i,j] = color_map[closest_color]
        output_path = os.path.join(output_folder, f"{os.path.basename(filename).split('.')[0]}_processed.png")
        Image.fromarray(pixels).save(output_path)

if __name__ == '__main__':
    map_pixels('average_colors.json', 'Images', 'Edited')