"""
yolo的类别id从0开始，coco的从1开始
coco的现在也从0开始呢
"""

import os
import random
import shutil
import yaml
import json
from PIL import Image
from common.constants import Constants

# index is coco id, list[coco id] = obj id

class CocoDatasetGenerator:
    def get_image_info(self, image_id, file_name, width, height):
        return {
            "id": image_id,
            "file_name": file_name,
            "width": width,
            "height": height
        }

    def get_annotation_info(self, annotation_id, image_id, coco_id, bbox):
        x, y, width, height = bbox
        area = width * height
        return {
            "id": annotation_id,
            "image_id": image_id,
            "category_id": coco_id,
            "bbox": [x, y, width, height],
            "area": area,
            "segmentation": [],
            "iscrowd": 0
        }

    def copy_and_rename_image(self, src, dst, image_id):
        new_file_name = f"{image_id}.png"
        new_file_path = os.path.join(dst, new_file_name)
        shutil.copy(src, new_file_path)
        return new_file_name

    def process_images_and_annotations(self, root_dir, coco_root):
        categories = []
        category_set = set()
        images = []
        annotations = []
        annotation_id = 1
        image_id = 1

        all_image_paths = []

        for scene_folder in os.listdir(root_dir):
            if scene_folder.startswith('scene'):
                scene_path = os.path.join(root_dir, scene_folder)
                rgb_folder = os.path.join(scene_path, 'rgb')
                bbox_file = os.path.join(scene_path, 'bbox.yml')

                with open(bbox_file, 'r') as f:
                    bboxes = yaml.safe_load(f)

                for file_name in os.listdir(rgb_folder):
                    if file_name.endswith('.png'):
                        img_id_str = os.path.splitext(file_name)[0]
                        img_bboxes = bboxes.get(img_id_str, [])
                        src_image_path = os.path.join(rgb_folder, file_name)

                        with Image.open(src_image_path) as img:
                            width, height = img.size

                        all_image_paths.append((src_image_path, img_bboxes, width, height))

        random.shuffle(all_image_paths)
        train_split = int(0.8 * len(all_image_paths))

        for idx, (src_image_path, img_bboxes, width, height) in enumerate(all_image_paths):
            split = 'train2017' if idx < train_split else 'val2017'
            image_output_dir = os.path.join(coco_root, split)
            os.makedirs(image_output_dir, exist_ok=True)

            new_file_name = self.copy_and_rename_image(src_image_path, image_output_dir, image_id)
            image_info = self.get_image_info(image_id, new_file_name, width, height)
            images.append(image_info)

            for obj in img_bboxes:
                category_id = obj['obj_id']
                if category_id not in Constants.dataset_objects_ids:
                    continue
                # id从1开始，不从0开始
                coco_id = Constants.dataset_objects_ids.index(category_id)
                bbox = obj['xywh']
                if category_id not in category_set:
                    categories.append({
                        "id": coco_id,
                        "name": "obj" + str(category_id),
                        "supercategory": "none"
                    })
                    category_set.add(category_id)

                annotation_info = self.get_annotation_info(annotation_id, image_id, coco_id, bbox)
                annotations.append(annotation_info)
                annotation_id += 1

            image_id += 1

        train_images = images[:train_split]
        val_images = images[train_split:]
        train_annotations = [ann for ann in annotations if ann['image_id'] <= train_split]
        val_annotations = [ann for ann in annotations if ann['image_id'] > train_split]

        coco_format_train = {
            "images": train_images,
            "annotations": train_annotations,
            "categories": categories
        }

        coco_format_val = {
            "images": val_images,
            "annotations": val_annotations,
            "categories": categories
        }

        os.makedirs(Constants.coco_annotations_dir, exist_ok=True)

        with open(os.path.join(Constants.coco_annotations_dir, 'instances_train2017.json'), 'w') as f:
            json.dump(coco_format_train, f, indent=4)


        with open(os.path.join(Constants.coco_annotations_dir, 'instances_val2017.json'), 'w') as f:
            json.dump(coco_format_val, f, indent=4)

if __name__ == "__main__":
    coco_dataset_generator = CocoDatasetGenerator()
    split = 'train2017'  # 或 'val2017' 根据你的数据集划分
    # 把rtless中的各个scene整合起来并且制作成coco格式
    coco_dataset_generator.process_images_and_annotations(Constants.rt_less_dir, Constants.coco_dir)
