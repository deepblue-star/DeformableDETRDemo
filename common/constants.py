import os


class Constants:
    """
    文件路径
    """
    data_root_dir = '/home/ubuntu/4T/zhz/object_detection/data'
    rt_less_dir = os.path.join(data_root_dir, "rt_less")

    coco_dir = os.path.join(data_root_dir, "coco", "coco_data")
    coco_annotations_dir = os.path.join(coco_dir, 'annotations')
    coco_validate_dir = os.path.join(data_root_dir, "coco", "coco_validate")

    voc_dir = os.path.join(data_root_dir, "voc", "voc_data")

    yolo_dir = os.path.join(data_root_dir, "yolo", "yolo_data")
    yolo_images_train_dir = os.path.join(yolo_dir, "images", "train")
    yolo_images_val_dir = os.path.join(yolo_dir, "images", "val")
    yolo_labels_train_dir = os.path.join(yolo_dir, "labels", "train")
    yolo_labels_val_dir = os.path.join(yolo_dir, "labels", "val")
    yolo_dataset_cfg_yml = os.path.join(yolo_dir, "my_yolo_cfg.yml")

    # 把rtless的目标贴图到linemod上，以此扩充rtless数据集，增加多样性
    # 最终结果保持和rtless一样的格式
    linemod_generate_dir = os.path.join(data_root_dir, "linemod")
    # linemod的目标文件夹，生成后的数据集在这
    # 生成前把rtless的scene复制到这里面
    linemod_dest_dir = os.path.join(linemod_generate_dir, "dest")
    linemod_base_dir = os.path.join(linemod_generate_dir, "base")

    labelme_data_dir = os.path.join(data_root_dir, "custom", "mixed")

    """
    数据集设置
    """
    # 选择rtless -> coco需要使用的obj
    # index is coco id, list[coco id] = obj id
    # dataset_objects_ids = [37, 6, 20, 12, 7, 8]
    dataset_objects_ids = [6, 7]
    dataset_objects_names = ["obj" + str(i) for i in dataset_objects_ids]
