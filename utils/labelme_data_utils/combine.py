import os
import shutil

# 源文件夹，包含多个子文件夹
source_folder = '/home/ubuntu/4T/zhz/object_detection/data/custom/20241023'
# 目标文件夹，存放合并后的文件
destination_folder = '/home/ubuntu/4T/zhz/object_detection/data/custom/mixed'

# 创建目标文件夹
os.makedirs(destination_folder, exist_ok=True)

# 创建目标文件夹
os.makedirs(destination_folder, exist_ok=True)

# 计数器，用于重新编号
counter = 0  # 从1开始编号

# 遍历源文件夹中的所有子文件夹
for root, dirs, files in os.walk(source_folder):
    for file in files:
        if file.endswith('.jpg'):
            # 找到对应的.json文件
            json_file = file.replace('.jpg', '.json')
            jpg_path = os.path.join(root, file)
            json_path = os.path.join(root, json_file)

            if os.path.exists(json_path):  # 确保.json文件存在
                # 新文件名
                new_jpg_name = f"{counter}.jpg"
                new_json_name = f"{counter}.json"

                # 拷贝文件到目标文件夹
                shutil.copy2(jpg_path, os.path.join(destination_folder, new_jpg_name))
                shutil.copy2(json_path, os.path.join(destination_folder, new_json_name))

                # 增加计数器
                counter += 1

print("文件合并完成，保持了对应关系！")