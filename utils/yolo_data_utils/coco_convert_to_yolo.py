"""
yolo的类别id从0开始，coco的从1开始
coco的现在也从0开始呢
"""
import json
import os
import shutil
import yaml
from tqdm import tqdm
from common.constants import Constants

coco_path = Constants.coco_dir
output_path = Constants.yolo_dir

os.makedirs(Constants.yolo_images_train_dir, exist_ok=True)
os.makedirs(Constants.yolo_images_val_dir, exist_ok=True)
os.makedirs(Constants.yolo_labels_train_dir, exist_ok=True)
os.makedirs(Constants.yolo_labels_val_dir, exist_ok=True)

with open(os.path.join(coco_path, "annotations", "instances_train2017.json"), "r") as f:
    train_annotations = json.load(f)

with open(os.path.join(coco_path, "annotations", "instances_val2017.json"), "r") as f:
    val_annotations = json.load(f)

# Iterate over the training images
for image in tqdm(train_annotations["images"]):
    width, height = image["width"], image["height"]
    scale_x = 1.0 / width
    scale_y = 1.0 / height

    label = ""
    for annotation in train_annotations["annotations"]:
        if annotation["image_id"] == image["id"]:
            # Convert the annotation to YOLO format
            x, y, w, h = annotation["bbox"]
            x_center = x + w / 2.0
            y_center = y + h / 2.0
            x_center *= scale_x
            y_center *= scale_y
            w *= scale_x
            h *= scale_y
            class_id = annotation["category_id"] - 1
            label += "{} {} {} {} {}\n".format(class_id, x_center, y_center, w, h)

    # Save the image and label
    shutil.copy(os.path.join(coco_path, "train2017", image["file_name"]),
                os.path.join(output_path, "images", "train", image["file_name"]))
    with open(os.path.join(output_path, "labels", "train", image["file_name"].replace(".jpg", ".txt")), "w") as f:
        f.write(label)

# Iterate over the validation images
for image in tqdm(val_annotations["images"]):
    width, height = image["width"], image["height"]
    scale_x = 1.0 / width
    scale_y = 1.0 / height

    label = ""
    for annotation in val_annotations["annotations"]:
        if annotation["image_id"] == image["id"]:
            # Convert the annotation to YOLO format
            x, y, w, h = annotation["bbox"]
            x_center = x + w / 2.0
            y_center = y + h / 2.0
            x_center *= scale_x
            y_center *= scale_y
            w *= scale_x
            h *= scale_y
            class_id = annotation["category_id"]
            label += "{} {} {} {} {}\n".format(class_id, x_center, y_center, w, h)

    # Save the image and label
    shutil.copy(os.path.join(coco_path, "val2017", image["file_name"]),
                os.path.join(output_path, "images", "val", image["file_name"]))
    with open(os.path.join(output_path, "labels", "val", image["file_name"].replace(".jpg", ".txt")), "w") as f:
        f.write(label)

# 创建YML文件的内容
yml_content = {
    'path': Constants.yolo_dir,
    'train': Constants.yolo_images_train_dir,
    'val': Constants.yolo_images_val_dir,
    'test': Constants.yolo_images_val_dir,
    'names': {i: name for i, name in enumerate(Constants.dataset_objects_names)},
    'nc': len(Constants.dataset_objects_ids)
}

# 将内容写入YML文件
with open(Constants.yolo_dataset_cfg_yml, 'w') as file:
    yaml.dump(yml_content, file, default_flow_style=False)
