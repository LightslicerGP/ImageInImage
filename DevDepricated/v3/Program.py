# pyinstaller --onefile v3\Program.py -c --console --nowindowed --name=Texture_to_Texture ; Rename-Item -Path ".\dist" -NewName "Final_Program" ; Remove-Item -Recurse -Force ".\build", ".\Texture_to_Texture.spec"

import os
import time
import json
import math
import platform
from PIL import Image

if platform.system() == "Windows":
    from colorama import init

    init()

debug = False

red = "\033[31m"
yellow = "\033[33m"
green = "\033[32m"
blue = "\033[34m"
bold = "\033[1m"
boldreset = "\033[22m"
reset = "\033[0m"


def get_average_color(folder_path, allow_transparency, skip_list_path):
    color_dict = {}
    with open(skip_list_path, "r") as f:
        skip_list = [line.strip() for line in f.readlines()]
    for file_name in os.listdir(folder_path):
        if file_name in skip_list:
            if debug:
                print(
                    file_name + ":", red + "Skipped due to being in skip list.", reset
                )
            continue
        if not file_name.lower().endswith((".png", ".jpg", ".jpeg")):
            continue
        with Image.open(os.path.join(folder_path, file_name)).convert("RGBA") as img:
            width, height = img.size
            empty_pixel = False
            for x in range(width):
                for y in range(height):
                    r, g, b, a = img.getpixel((x, y))
                    if a <= 1:
                        empty_pixel = True
                        break
                if empty_pixel:
                    break
            color = img.resize((1, 1)).getpixel((0, 0))
            hex_color = "#{0:02x}{1:02x}{2:02x}{3:02x}".format(*color)
            if hex_color.endswith("ff", 7, 9):
                if debug:
                    print(file_name + ":", hex_color)
                    print(green + "Solid texture, added.", reset)
                hex_color = "#{0:02x}{1:02x}{2:02x}".format(*color)
            elif not hex_color.endswith("ff", 7, 9) and not allow_transparency:
                if debug:
                    print(file_name + ":", hex_color)
                    print(red + "Unsolid texture, skipped.", reset)
                continue
            elif not hex_color.endswith("ff", 7, 9) and allow_transparency:
                if debug:
                    print(file_name + ":", hex_color)
                    print(yellow + "Unsolid texture, included.", reset)
                hex_color = "#{0:02x}{1:02x}{2:02x}".format(*color)
            file_path = os.path.join(folder_path, file_name)
            if not empty_pixel:
                color_dict[hex_color] = file_path
            if empty_pixel:
                if debug:
                    print(hex_color)
                    print(
                        blue
                        + "Texture has an empty and/or fully transparent pixel, skipped.",
                        reset,
                    )
    with open("average_colors.json", "w") as f:
        json.dump(color_dict, f, indent=4)


def get_distance(color1, color2):
    r1, g1, b1 = color1
    r2, g2, b2, a2 = color2
    return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2 + a2)


def find_nearest_color(json_file, target_color):
    nearest_color = None
    nearest_distance = float("inf")
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
    hex_value = hex_color.lstrip("#")
    if len(hex_value) == 6:
        color_tuple = tuple(int(hex_value[i : i + 2], 16) for i in (0, 2, 4))
    elif len(hex_value) == 8:
        color_tuple = tuple(int(hex_value[i : i + 2], 16) for i in (0, 2, 4, 8))
    return color_tuple


def image_creation(ref_image_path, ref_json_file, dest_folder):
    with Image.open(ref_image_path).convert("RGBA") as ref_image:
        width, height = ref_image.size
        final_dimensions = (width * 16, height * 16)
        final_image = Image.new("RGBA", final_dimensions)
        if debug:
            print(yellow + f"Processing {os.path.basename(ref_image_path)}...", reset)
        for x in range(width):
            for y in range(height):
                color_rgb = ref_image.getpixel((x, y))[:4]
                pixel_opacity = ref_image.getpixel((x, y))[3]
                paste_image_path = find_nearest_color(ref_json_file, color_rgb)[1]
                with Image.open(paste_image_path) as paste_image:
                    if paste_image.size != (16, 16):
                        paste_image = paste_image.crop((0, 0, 16, 16))
                    paste_image = paste_image.convert("RGBA")
                    paste_image.putalpha(pixel_opacity)
                    final_image.paste(paste_image, (x * 16, y * 16))
        final_image.save(os.path.join(dest_folder, os.path.basename(ref_image_path)))
        if debug:
            print(
                green + f"{os.path.basename(ref_image_path)} has been processed!", reset
            )


def convert(ref_json, ref_folder, current_file, dest_folder):
    if current_file.lower().endswith((".png", ".jpg", ".jpeg")):
        ref_image_path = os.path.join(ref_folder, current_file)
        image_creation(ref_image_path, ref_json, dest_folder)


print("Starting up...")

folders = ["Base Textures", "Reference Textures", "Final Textures"]
ref_skip_file = "reference texture skip list.txt"
for folder in folders:
    try:
        if not os.path.exists(folder):
            os.mkdir(folder)
            print(yellow + f'Folder "{folder}" not found, created folder.', reset)
        else:
            print(green + f'Folder "{folder}" found.', reset)
    except OSError:
        print(red + f'Folder "{folder}" not able to be made.', reset)
        time.sleep(3)
        exit()
if os.path.exists(ref_skip_file):
    print(green + f'File "{ref_skip_file}" found.', reset)
else:
    open(ref_skip_file, "w")
    print(yellow + f'File "{ref_skip_file}" not found, created file.', reset)

print(
    "This program allows you to have a texture have textures inside as a replacement for each pixel, this program has been mainly used in my (LightslicerGP's) Blocks in Blocks Reimagined Rescource Pack since the original is only updated to 1.15! So this program aims to fix that, and allow others to do the same!\n\nThis program takes the files from \\Reference Textures\\ and gets each texture's average color, and saves it in a json list to use later. (these images are cropped into the top left 16x16 pixels for easy use)\n\nThen it takes the images from \\Base Textures\\ as the textures to \"upscale\" to 256x256 with each pixel from the original texture replaced by another entire texture from the json that uses the files in \\Reference Textures\\\n\nPlease remove any textures (that are not translucent, since they can be filtered as an option in a moment) such as stage textures like frosted ice stage 2, or the debug textures, or lit campfire textures, in case if you dont want them to be used as pixel replacements on the final images\n\nFinally, all the images will be stored in the \\Final Textures\\ folder! After processing the json, be aware that there is another prompt for confirmation before the textures themselves will be processed!"
)
input(
    f"Please place in the desired files in \\Base Textures\\ and \\Reference Textures\\ now, alongside any files you dont want to be used as reference files in \\reference texture skip list.txt\\, one file every line. {yellow}Make sure to remove any textures you dont want to be used beforehand!{reset} To continue, press enter."
)

allow_translucency_input = input(
    "Do you want to allow translucent textures? E.g. Stained glass. (This will not allow textures like saplings or the copper rod texture) y/n: "
)
if allow_translucency_input.lower() in ["y", "yes"]:
    allow_translucency = True
elif allow_translucency_input.lower() in ["n", "no"]:
    allow_translucency = False
else:
    print("Improper input, operation cancelled.")
    time.sleep(1)
    exit()

print(
    bold
    + red
    + 'WARNING! THIS WILL EMPTY YOUR "Final Textures" FOLDER, PLEASE REMOVE ANY FILES INSIDE BEFORE CONTINUING!',
    boldreset,
    reset,
)
input("To continue, press enter.")

print(
    f"Processing will begin in 5 seconds, {bold}{red}DO NOT MOVE FILES AND/OR FOLDERS DURING THIS PROCESS!{boldreset}{reset}"
)
time.sleep(5)

get_average_color(
    "Reference Textures", allow_translucency, "reference texture skip list.txt"
)
print(green + "Color directory json created!", reset)

input(
    f"\nTexture processing will begin, {yellow}this will take some time, the more files, the longer this will take!{red} MAKE SURE TO NOT CLOSE THE PROGRAM WHILE IT IS RUNNING, you will need to restart by doing so.{reset} If you would like to continue, press enter."
)
directory_path = "Base Textures"
start_time = time.time()
for filename in os.listdir(directory_path):
    if os.path.isfile(os.path.join(directory_path, filename)):
        convert("average_colors.json", directory_path, filename, "Final Textures")

elapsed_time = time.time() - start_time
hours = int(elapsed_time // 3600)
minutes = int((elapsed_time % 3600) // 60)
seconds = int(elapsed_time % 60)
current_time = time.strftime("%Y-%m-%d %H:%M:%S")
print(
    f"Processing time: {hours} hours, {minutes} minutes, {seconds} seconds\nEnding time time: {current_time}"
)
