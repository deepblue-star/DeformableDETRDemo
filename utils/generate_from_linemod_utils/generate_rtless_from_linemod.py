import yaml
import os
import cv2
import random
import numpy as np
from common.constants import Constants


def overlay_image_with_mask(img, sub_img, mask, top_left_x, top_left_y):
    """
    将 sub_img 中通过 mask 指定的部分叠加到 img 的指定位置。

    参数:
    img (numpy.ndarray): 目标图像，形状为 (x, y, 3)。
    sub_img (numpy.ndarray): 需要叠加的子图像，形状为 (x1, y1, 3)。
    mask (numpy.ndarray): 掩码图像，形状为 (x1, y1)，值为 0 或 255。
    top_left_x (int): 要叠加到 img 中的位置的左上角 x 坐标。
    top_left_y (int): 要叠加到 img 中的位置的左上角 y 坐标。

    返回:
    result (numpy.ndarray): 叠加后的图像。
    """
    # 获取子图像的尺寸
    x1, y1 = sub_img.shape[:2]

    # 创建一个区域用于放置子图像
    roi = img[top_left_y:top_left_y + x1, top_left_x:top_left_x + y1]

    # 将 mask 应用于 sub_img 和 roi
    sub_img_masked = cv2.bitwise_and(sub_img, sub_img, mask=mask)
    roi_masked = cv2.bitwise_and(roi, roi, mask=cv2.bitwise_not(mask))

    # 合并两个部分
    dst = cv2.add(sub_img_masked, roi_masked)

    # 将结果放回原图的对应位置
    img[top_left_y:top_left_y + x1, top_left_x:top_left_x + y1] = dst

    return img


def binarize_image(image):
    """
    将黑白图片进行二值化处理。

    参数:
    image (numpy.ndarray): 输入图像，形状为 (x, y, 3)。

    返回:
    binary_image (numpy.ndarray): 二值化后的图像，形状为 (x, y)。
    """
    # 将形状为 (x, y, 3) 的图像转换为灰度图像 (x, y)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 创建一个二值化后的图像矩阵，初始值为0
    binary_image = np.zeros_like(gray_image)

    # 将大于等于1的像素值设置为255
    binary_image[gray_image >= 1] = 255

    return binary_image


def find_max_jpg_number(folder_path):
    max_number = 0

    # 获取文件夹中所有的.jpg文件
    jpg_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.jpg')]

    # 遍历所有.jpg文件，提取数字并找到最大值
    for jpg_file in jpg_files:
        # 提取文件名中的数字部分
        try:
            number = int(os.path.splitext(jpg_file)[0])
            if number > max_number:
                max_number = number
        except ValueError:
            # 如果文件名不是纯数字，跳过
            continue

    return max_number


def get_random_jpg(folder_path):
    # 获取文件夹中所有的.jpg文件
    jpg_files = [f for f in os.listdir(folder_path) if
                 os.path.isfile(os.path.join(folder_path, f)) and f.lower().endswith('.jpg')]

    png_files = [f for f in os.listdir(folder_path) if
                 os.path.isfile(os.path.join(folder_path, f)) and f.lower().endswith('.png')]

    # 检查是否有.jpg文件
    if not jpg_files and not png_files:
        raise FileNotFoundError("No .jpg or .png files found in the specified folder.")

    jpg_files = jpg_files + png_files
    # 从中随机抽取一个文件
    random_file = random.choice(jpg_files)
    picked_img = cv2.imread(os.path.join(folder_path, random_file))

    return picked_img


def find_scene_folders(path):
    scene_folders = []

    # 遍历指定路径下的所有文件和文件夹
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        # 检查是否为目录且名称以"scene"开头
        if os.path.isdir(item_path) and item.startswith("scene"):
            scene_folders.append(item)

    return scene_folders


def find_jpg_files(folder_path):
    jpg_files = []

    # 遍历指定路径下的所有文件
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        # 检查是否为文件且扩展名为.jpg
        if os.path.isfile(item_path) and item.lower().endswith('.jpg'):
            jpg_files.append(item)

    return jpg_files


def read_bbox_yml(yml_file):
    # 读取yml文件
    with open(yml_file, 'r') as file:
        bbox_data = yaml.safe_load(file)
    return bbox_data


def save_bbox_yml(data, yml_file):
    with open(yml_file, 'w') as file:
        yaml.safe_dump(data, file)


# 1 找到所有scene
# 2 遍历scene
    # 在每个scene中
    # 1 遍历每张图片
    # 2 每张图片随机抽取1个零件
    # 3 根据bbox.yml读取零件bbox
    # 4 截取图像
    # 5 做resize/模糊/遮挡等增强
    # 6 从linemod基底文件夹中选择图片
    # 7 将截取图像随机贴图到基底图片上
    # 8 保存图片到rgb文件夹末尾
    # 9 追加新bbox到bbox.yml结尾
# 3 保存bbox.yml
def main():
    linemod_dest_dir = Constants.linemod_dest_dir
    linemod_base_dir = Constants.linemod_base_dir
    scene_list = find_scene_folders(linemod_dest_dir)
    for scene in scene_list:
        scene_dir = os.path.join(linemod_dest_dir, scene)
        bbox_yml_dir = os.path.join(scene_dir, "bbox.yml")
        rgb_dir = os.path.join(scene_dir, "rgb")
        bbox_dict = read_bbox_yml(bbox_yml_dir)
        img_names = find_jpg_files(rgb_dir)
        for img_name in img_names:
            # 随机抽取rtless图片中的一个零件，截取出来
            img_index = img_name.rsplit('.', 1)[0]
            img_dir = os.path.join(rgb_dir, img_name)
            source_img = cv2.imread(img_dir)

            obj_nums = len(bbox_dict[img_index])
            obj_dict = bbox_dict[img_index][random.randint(0, obj_nums - 1)]
            obj_id = obj_dict["obj_id"]
            xywh = obj_dict["xywh"]
            x, y, w, h = xywh
            clip_img = source_img[y: y + h, x: x + w]

            # 抽取mask
            mask_dir = os.path.join(scene_dir, "mask", img_index + "_" + str(obj_id) + ".png")
            mask = cv2.imread(mask_dir)
            clip_mask = mask[y: y+h, x: x+w]

            # 随机从基底文件夹中抽取一张基底图片
            picked_img = get_random_jpg(linemod_base_dir)

            # resize
            resize_scale = random.uniform(0.4, 1)
            clip_img = cv2.resize(clip_img, (int(resize_scale * w), int(resize_scale * h)), interpolation=cv2.INTER_CUBIC)
            clip_mask = cv2.resize(clip_mask, (int(resize_scale * w), int(resize_scale * h)), interpolation=cv2.INTER_CUBIC)
            clip_mask = binarize_image(clip_mask)

            # 贴图
            new_w = clip_img.shape[1]
            new_h = clip_img.shape[0]
            new_x = random.randint(0, picked_img.shape[1] - new_w - 1)
            new_y = random.randint(0, picked_img.shape[0] - new_h - 1)
            new_xywh = [new_x, new_y, new_w, new_h]
            synthetic_img = picked_img.copy()
            # synthetic_img[new_y: new_y + new_h, new_x: new_x + new_w] = clip_img
            synthetic_img = overlay_image_with_mask(synthetic_img, clip_img, clip_mask, new_x, new_y)

            # 找到rgb文件夹的图片中，数字最大的文件名，把合成图片追加到文件夹最后
            synthetic_img_id = find_max_jpg_number(rgb_dir) + 1
            cv2.imwrite(os.path.join(rgb_dir, str(synthetic_img_id) + ".jpg"), synthetic_img)

            # 追加图片信息到yml结尾
            synthetic_img_obj_list = []
            synthetic_img_obj_list.append({"obj_id": obj_id, "xywh": new_xywh})
            bbox_dict[str(synthetic_img_id)] = synthetic_img_obj_list
        save_bbox_yml(bbox_dict, bbox_yml_dir)


# 使用方法
if __name__ == "__main__":
    main()

