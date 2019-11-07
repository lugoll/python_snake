from pygame import image
from pathlib import Path

import settings

block_image = image.load(str(Path(settings.image_directory + 'block.png')))
ground_image = image.load(str(Path(settings.image_directory + 'ground.png')))
snake_image = image.load(str(Path(settings.image_directory + 'snake.png')))
pineapple_image = image.load(str(Path(settings.image_directory + 'pineapple.png')))



