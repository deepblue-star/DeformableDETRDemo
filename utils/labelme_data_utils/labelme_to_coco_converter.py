import os
import json
import random
import shutil

from common.constants import Constants


def create_coco_json(images, annotations, categories, output_file):
    coco_format = {
        "images": images,
        "annotations": annotations,
        "categories": categories
    }
    os.makedirs(os.path.dirname(output_file), exist_ok=True)  # 确保目录存在
    with open(output_file, 'w') as json_file:
        json.dump(coco_format, json_file, indent=4)


def convert_labelme_to_coco(labelme_dir, train_dir, val_dir, train_ratio=0.8):
    images_train = []
    annotations_train = []
    images_val = []
    annotations_val = []
    categories = []
    img_id = 0
    ann_id = 0
    category_id = 0  # 从0开始

    # 获取所有标注文件
    labelme_files = [f for f in os.listdir(labelme_dir) if f.endswith('.json')]
    random.shuffle(labelme_files)  # 打乱顺序

    # 计算分割索引
    train_count = int(len(labelme_files) * train_ratio)

    # 遍历标注文件
    for idx, json_file in enumerate(labelme_files):
        is_train = idx < train_count
        target_dir = train_dir if is_train else val_dir
        images = images_train if is_train else images_val
        annotations = annotations_train if is_train else annotations_val

        with open(os.path.join(labelme_dir, json_file), 'r') as f:
            labelme_data = json.load(f)

        img_name = json_file[:-4] + "jpg"
        img_width = labelme_data['imageWidth']
        img_height = labelme_data['imageHeight']

        # 将图像复制到目标文件夹
        shutil.copy(os.path.join(labelme_dir, img_name), os.path.join(target_dir, img_name))

        # 添加图像信息
        img_id += 1
        images.append({
            "id": img_id,
            "file_name": img_name,
            "width": img_width,
            "height": img_height
        })

        # 遍历标注信息
        for shape in labelme_data['shapes']:
            label = shape['label']
            if label not in Constants.dataset_objects_names:
                continue
            if label not in [cat['name'] for cat in categories]:
                categories.append({
                    "id": category_id,
                    "name": label,
                    "supercategory": "none"  # 添加supercategory字段
                })
                category_id += 1

            # 提取边界框（bbox）
            points = shape['points']
            x_min = min(p[0] for p in points)
            y_min = min(p[1] for p in points)
            x_max = max(p[0] for p in points)
            y_max = max(p[1] for p in points)
            width = x_max - x_min
            height = y_max - y_min

            # 添加注释信息
            annotations.append({
                "id": ann_id,
                "image_id": img_id,
                "category_id": next(cat['id'] for cat in categories if cat['name'] == label),
                "bbox": [x_min, y_min, width, height],
                "area": width * height,
                "segmentation": [],  # 空数组
                "iscrowd": 0
            })
            ann_id += 1

    # 创建COCO格式JSON文件
    create_coco_json(images_train, annotations_train, categories, train_json_dir)
    create_coco_json(images_val, annotations_val, categories, val_json_dir)


# 设置路径和比例
coco_dir = Constants.coco_dir
train_dir = os.path.join(coco_dir, 'train2017')
train_json_dir = os.path.join(coco_dir, "annotations", "instances_train2017.json")

val_dir = os.path.join(coco_dir, 'val2017')
val_json_dir = os.path.join(coco_dir, "annotations", "instances_val2017.json")

train_ratio = 0.8  # 设置训练集比例

# 创建训练和验证集目录
os.makedirs(train_dir, exist_ok=True)
os.makedirs(val_dir, exist_ok=True)
os.makedirs(os.path.join(coco_dir, "annotations"))

# 调用转换函数
convert_labelme_to_coco(Constants.labelme_data_dir, train_dir, val_dir, train_ratio=0.8)
