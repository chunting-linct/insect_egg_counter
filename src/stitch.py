import cv2
from cv2.cuda import ensureSizeIsEnough
import numpy as np
import os
path = "b3"

def estimate_offset(img1, img2):
    img1 = cv2.imread(img1, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(img2, cv2.IMREAD_GRAYSCALE)

    shift, _ = cv2.phaseCorrelate(np.float32(img1), np.float32(img2))
    return shift


file_list = [file for file in os.listdir(path)]
file_list.sort()
h = 480
w = 640

offset_list = []

for i, file in enumerate(file_list):
    if i > 0:
        offx, offy = estimate_offset(os.path.join(path, file_list[i - 1]),os.path.join(path, file_list[i]))
        print(file_list[i], offx, offy)
        offset_list.append((int(offx), int(offy)))

"""


x = 0
y = 0
min_x , min_y, max_x, max_y = 0, 0, 0, 0
axis_list = [(0, 0)]
for offset in offset_list:
    x -= offset[0]
    y -= offset[1]
    max_x = max(max_x, x)
    max_y = max(max_y, y)
    min_x = min(min_x, x)
    min_y = min(min_y, y)
    axis_list.append((x, y))
axis_list = [(axis[0] - min_x, axis[1] - min_y) for axis in axis_list]
mosaic = np.zeros((max_y - min_y + h, max_x - min_x + w, 3), dtype=np.float32)
weight = np.zeros((max_y - min_y + h, max_x - min_x + w, 3), dtype=np.float32)
winner = -np.ones((max_y - min_y + h, max_x - min_x + w), dtype=np.float32)
y = np.linspace(-1, 1, h)[:, None]
y = np.linspace(-1, 1, h)[:, None]
x = np.linspace(-1, 1, w)[None, :]
mask = (1 - np.abs(x)) * (1 - np.abs(y))   
mask = mask 
mask = np.clip(mask, 0, 1).astype(np.float32)
mask_3 = np.stack([mask, mask, mask], axis=-1)
for i, file in enumerate(file_list):

    img = cv2.imread(os.path.join(path, file))
    if img is None:
        print(f"Cannot read")
        continue  # skip missing image
    img_f = img.astype(np.float32)
    illum = cv2.GaussianBlur(img_f, (101, 101), 0)
    illum_mean = np.mean(illum, axis=(0,1), keepdims=True)

    img_corrected = img_f / (illum / (illum_mean + 1e-6))

    img = np.clip(img_corrected, 0, 255).astype(np.uint8)
    x, y = axis_list[i]
    W = winner[y : y + 480, x : x + 640] 
    winner_mask = mask > W
    edge_mask = np.abs(mask - W) < 0.0005
    edge_zero = np.zeros(W.shape)
    edge_zero[edge_mask] = (mask - W)[edge_mask]
    if edge_zero.max() - edge_zero.min() > 0:
        edge_zero = (edge_zero - edge_zero.min()) / (edge_zero.max() - edge_zero.min())
    



    edge_mask_3 = np.repeat(edge_mask[:, :, None], 3, axis=2)
    edge_zero_3 = np.repeat(edge_zero[:, :, None], 3, axis=2)


    





    W[winner_mask] = mask[winner_mask]








    winner_mask_3 = np.repeat(winner_mask[:, :, None], 3, axis=2)
    

    
    M = mosaic[y : y + 480, x : x + 640] 
    M[winner_mask_3] = img[winner_mask_3]

    M[edge_mask_3] = img[edge_mask_3] * edge_zero_3[edge_mask_3] + M[edge_mask_3] * (1 - edge_zero_3[edge_mask_3])

#mosaic = mosaic / np.maximum(weight, 1e-25)

cv2.imwrite("mosica_b3.jpg", mosaic)
"""

