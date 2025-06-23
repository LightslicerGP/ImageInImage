# ImageInImage

Python Script to replace each pixel in an image with an image that has the average color closest to that pixel

This is used to make the BlocksInBlocks Renewed texture pack

## How to use

### Folders

- `Base Textures`: Images that will be resulted after the transformation/modification
- `Final Textures`: The final result, should have the same files (atleast images) and folders as `Base Textures`
- `Reference Textures`: Images that will be put onto/applied to the `Base Textures` images

### Files

- `Average Colors`: A json dictionary that holds the average color of each image(path), this is usually automatically generated based on the items in the `Base Textures` folder
- `Ignore Folders`: A list of folders the program will skip when processing (it will skip every folder with that name, not just in a specific path, might fix this)
- `Reference texture skip list`: Images that will be skipped when making the `Average Colors` dictionary file

### Variables

- `reference_images_folder`: Images that will be placed onto each pixel based on its average color value (default: `Reference Textures`)
- `color_dictionary`: Dictionary of images in the `reference_images_folder` and their average color value (default: `average_colors.json`)
- `ref_texture_skip_list`: A list of images to skip when making the `color_dictionary` file (default: `reference texture skip list.txt`)
- `allow_translucency`: allows transluscent images in the `reference_images_folder` (`ref_texture_skip_list` items will _still_ be ignored) to be in the `color_dictionary` file (default: `False`)

## How it works

This script first goes through each image in the `Reference Textures` folder (not any subfolders, just root level files, also skipping files in the `ref_texture_skip_list`) and gets each pixel in the image, and gets its average color saves it in `color_dictionary`.
Then it goes through each `Base Textures` folder (and subfolder) and makes an image 16x the original image size (assuming a 16x "default" texture pack resolution, _might make this able to work with larger images in the future_) and for each pixel in the original image, the script goes through every item in the `color_dictionary` file to see whatever color is closest, and then copies and pastes the image into the canvas. At the end of each image, the script saves the canvas as an image in the `Final Textures` Folder
