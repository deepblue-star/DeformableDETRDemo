import os
import json
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from common.constants import Constants


def draw_bounding_box(draw, bbox, category_name, color, font):
    x, y, width, height = bbox
    draw.rectangle([x, y, x + width, y + height], outline=color, width=2)
    text_size = draw.textsize(category_name, font=font)
    text_background = Image.new('RGBA', (text_size[0], text_size[1]), color + (255,))
    draw.rectangle([x, y - text_size[1], x + text_size[0], y], fill=color)
    draw.text((x, y - text_size[1]), category_name, fill="black", font=font)


def load_coco_annotations(json_path):
    with open(json_path, 'r') as f:
        annotations = json.load(f)
    return annotations


def process_images_with_annotations(coco_root, output_dir):
    annotations_dir = os.path.join(coco_root, 'annotations')
    os.makedirs(output_dir, exist_ok=True)

    json_files = [f for f in os.listdir(annotations_dir) if f.endswith('.json')]

    for json_file in json_files:
        annotations = load_coco_annotations(os.path.join(annotations_dir, json_file))
        images_info = {image['id']: image for image in annotations['images']}
        categories_info = {category['id']: category['name'] for category in annotations['categories']}
        image_annotations = {}

        for ann in annotations['annotations']:
            image_id = ann['image_id']
            if image_id not in image_annotations:
                image_annotations[image_id] = []
            image_annotations[image_id].append(ann)

        for image_id, anns in image_annotations.items():
            image_info = images_info[image_id]
            image_path = os.path.join(coco_root, json_file.replace('instances_', '').replace('.json', ''),
                                      image_info['file_name'])

            with Image.open(image_path) as img:
                draw = ImageDraw.Draw(img)
                font = ImageFont.load_default()

                for ann in anns:
                    category_id = ann['category_id']
                    bbox = ann['bbox']
                    category_name = categories_info[category_id]
                    color = tuple(np.random.randint(0, 256, 3).tolist())  # Random color for each category
                    draw_bounding_box(draw, bbox, category_name, color, font)

                output_image_path = os.path.join(output_dir, image_info['file_name'])
                img.save(output_image_path)


process_images_with_annotations(Constants.coco_dir, Constants.coco_validate_dir)
