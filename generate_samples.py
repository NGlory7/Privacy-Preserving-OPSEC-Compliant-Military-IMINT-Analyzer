"""
Synthetic Camouflage Sample Generator
Creates test swatch images for offline demonstration and testing.
"""

import os
import random
import numpy as np
from PIL import Image, ImageDraw

def generate_samples(output_dir: str):
    os.makedirs(output_dir, exist_ok=True)

    # 1. MultiCam Style Synthetic Swatch
    mc_colors = [(84, 79, 61), (124, 117, 88), (158, 148, 116), (59, 54, 40), (122, 107, 79)]
    img_mc = Image.new("RGB", (400, 400), mc_colors[0])
    draw_mc = ImageDraw.Draw(img_mc)
    for _ in range(60):
        c = random.choice(mc_colors)
        x = random.randint(0, 360)
        y = random.randint(0, 360)
        r = random.randint(25, 75)
        draw_mc.ellipse([x, y, x + r, y + int(r * 0.7)], fill=c)
    img_mc.save(os.path.join(output_dir, "sample_multicam.png"))

    # 2. EMR / Digital Flora Style Synthetic Swatch
    emr_colors = [(45, 58, 39), (28, 36, 23), (67, 88, 53), (143, 134, 100), (15, 20, 14)]
    img_emr = Image.new("RGB", (400, 400), emr_colors[0])
    draw_emr = ImageDraw.Draw(img_emr)
    block_size = 10
    for bx in range(0, 400, block_size):
        for by in range(0, 400, block_size):
            if random.random() > 0.4:
                c = random.choice(emr_colors)
                draw_emr.rectangle([bx, by, bx + block_size, by + block_size], fill=c)
    img_emr.save(os.path.join(output_dir, "sample_emr_digital_flora.png"))

    # 3. Flecktarn Style Synthetic Swatch
    fleck_colors = [(49, 61, 41), (85, 107, 47), (43, 35, 25), (139, 125, 107), (20, 23, 19)]
    img_fleck = Image.new("RGB", (400, 400), fleck_colors[0])
    draw_fleck = ImageDraw.Draw(img_fleck)
    for _ in range(250):
        c = random.choice(fleck_colors)
        x = random.randint(0, 380)
        y = random.randint(0, 380)
        s = random.randint(6, 18)
        draw_fleck.ellipse([x, y, x + s, y + s], fill=c)
    img_fleck.save(os.path.join(output_dir, "sample_flecktarn.png"))

    # 4. TSK Turkish Digital Style Synthetic Swatch
    tsk_colors = [(90, 92, 70), (125, 120, 90), (155, 146, 115), (58, 56, 44)]
    img_tsk = Image.new("RGB", (400, 400), tsk_colors[0])
    draw_tsk = ImageDraw.Draw(img_tsk)
    for bx in range(0, 400, 8):
        for by in range(0, 400, 8):
            if random.random() > 0.35:
                c = random.choice(tsk_colors)
                draw_tsk.rectangle([bx, by, bx + 8, by + 8], fill=c)
    img_tsk.save(os.path.join(output_dir, "sample_turkish_digital.png"))

    print("Synthetic samples successfully created in:", output_dir)

if __name__ == "__main__":
    generate_samples(os.path.join(os.path.dirname(__file__), "data", "sample_images"))
