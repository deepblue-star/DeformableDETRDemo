import torch
import os

# model root path
root_path = '/home/ubuntu/user/zhanghaozheng/Deformable-DETR-main/Deformable-DETR-main-repo/converted_pretrained_model'
model1 = torch.load(os.path.join(root_path, "detr-r50-e632da11.pth"))

# 要检测的目标类别数量 + 1，有6种物体，那就是7
num_class = 2
model1["model"]["class_embed.weight"].resize_(num_class+1, 256)
model1["model"]["class_embed.bias"].resize_(num_class+1)
torch.save(model1, os.path.join(root_path, "detr-r50_test_%d.pth"%num_class))
