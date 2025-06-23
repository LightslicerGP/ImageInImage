from PIL import Image
import shutil
import os
import time
import json

base_images_folder = "Base Textures"
final_images_folder = "Final Textures"
folder_skip_list = "ignoreFolders.txt"
debug = False

reference_images_folder = "Reference Textures"
color_dictionary = "average_colors.json"
ref_texture_skip_list = "reference texture skip list.txt"

allow_translucency = False


if not os.path.exists(base_images_folder):
    os.makedirs(base_images_folder)
if not os.path.exists(final_images_folder):
    os.makedirs(final_images_folder)
if not os.path.exists(reference_images_folder):
    os.makedirs(reference_images_folder)


with open(folder_skip_list, "r") as file:
    ignore_folders = set(line.strip() for line in file.readlines())


def generate_color_dictionary():
    color_dict = {}

    with open(ref_texture_skip_list, "r") as f:
        skip_list = [line.strip() for line in f.readlines()]

    for file_name in os.listdir(reference_images_folder):
        if file_name in skip_list:
            continue
        if not file_name.lower().endswith((".png", ".jpg", ".jpeg")):
            continue

        with Image.open(os.path.join(reference_images_folder, file_name)).convert(
            "RGBA"
        ) as img:
            width, height = img.size
            empty_pixel = False
            for x in range(width):
                for y in range(height):
                    _, _, _, a = img.getpixel((x, y))
                    if a <= 1:
                        empty_pixel = True
                        break
                if empty_pixel:
                    break
            color = img.resize((1, 1)).getpixel((0, 0))
            hex_color = "#{0:02x}{1:02x}{2:02x}{3:02x}".format(*color)
            if hex_color.endswith("ff", 7, 9):
                hex_color = "#{0:02x}{1:02x}{2:02x}".format(*color)
            elif not hex_color.endswith("ff", 7, 9) and not allow_translucency:
                continue
            elif not hex_color.endswith("ff", 7, 9) and allow_translucency:
                hex_color = "#{0:02x}{1:02x}{2:02x}".format(*color)
            file_path = os.path.join(reference_images_folder, file_name)
            if not empty_pixel:
                color_dict[hex_color] = file_path
    with open(color_dictionary, "w") as f:
        json.dump(color_dict, f, indent=4)


def process_image(input_path, output_path):
    print(f"'{output_path}'") if debug else None
    with Image.open(input_path).convert("RGBA") as ref_image:
        width, height = ref_image.size
        final_dimensions = (width * 16, height * 16)
        final_image = Image.new("RGBA", final_dimensions)
        for x in range(width):
            for y in range(height):
                color_rgb = ref_image.getpixel((x, y))[:4]
                pixel_opacity = ref_image.getpixel((x, y))[3]

                nearest_color = None
                nearest_distance = float("inf")
                paste_image_path = None
                with open(color_dictionary) as f:
                    color_dict = json.load(f)
                for hex_color, file_path in color_dict.items():

                    hex_value = hex_color.lstrip("#")

                    if len(hex_value) == 6:
                        hex_tuple = tuple(
                            int(hex_value[i : i + 2], 16) for i in (0, 2, 4)
                        )
                    elif len(hex_value) == 8:
                        hex_tuple = tuple(
                            int(hex_value[i : i + 2], 16) for i in (0, 2, 4, 8)
                        )

                    r1, g1, b1 = hex_tuple
                    r2, g2, b2, a2 = color_rgb

                    distance = (
                        (r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2 + a2**2
                    ) ** 0.5
                    if distance < nearest_distance:
                        nearest_color = hex_tuple
                        nearest_distance = distance
                        paste_image_path = file_path

                with Image.open(paste_image_path) as paste_image:
                    if paste_image.size != (16, 16):
                        paste_image = paste_image.crop((0, 0, 16, 16))
                    paste_image = paste_image.convert("RGBA")
                    paste_image.putalpha(pixel_opacity)
                    final_image.paste(paste_image, (x * 16, y * 16))
        final_image.save(output_path)


def process_directory(base_images_folder, final_images_folder):
    if not os.path.exists(final_images_folder):
        os.makedirs(final_images_folder)
    for item in os.listdir(base_images_folder):
        if item in ignore_folders:
            continue
        source_path = os.path.join(base_images_folder, item)
        target_path = os.path.join(final_images_folder, item)
        if os.path.isdir(source_path):
            process_directory(source_path, target_path)
        elif item.endswith(".png"):
            process_image(source_path, target_path)
        elif item.endswith(".mcmeta"):
            shutil.copy2(source_path, target_path)


start = time.time()

print(f"creating {color_dictionary} data...") if debug else None
generate_color_dictionary()
print(f"processing textures...") if debug else None
process_directory(base_images_folder, final_images_folder)
print("done") if debug else None

end = time.time()
total = end - start
(
    print(
        f"{int(total // 3600)}h {int((total % 3600) // 60)}m {int(total % 60)}s {int((total - int(total)) * 1000)}ms"
    )
    if debug
    else None
)
