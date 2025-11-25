import cv2
from cv2.cuda import ensureSizeIsEnough
import numpy as np
import os
path = "images"

def estimate_offset(img1, img2):
    img1 = cv2.imread(img1, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(img2, cv2.IMREAD_GRAYSCALE)

    shift, _ = cv2.phaseCorrelate(np.float32(img1), np.float32(img2))
    return shift

def name_generator(row, col):
    return str(row).zfill(4) + '_' + str(col).zfill(4) + '.jpg'




file_list = [file for file in os.listdir(path)]
file_list.sort()
h = 480
w = 640

offset_list = []
count = 1


axis_list = []
col_ref = (110, -20)
row_ref = (-15, -64)

for file in file_list:
    name_part = file.split('.')[0]
    row = int(name_part.split('_')[0])
    col = int(name_part.split('_')[1])
    if col == 0:
        axis_list.append([])
        if row == 0:
            axis_list[-1].append((0, 0))
        else:
            file_1 = os.path.join(path, name_generator(row-1, col))
            file_2= os.path.join(path, file)
            offx, offy = estimate_offset(file_1, file_2)
            if abs(offx - row_ref[0]) + abs(offy - row_ref[1]) > 20:
                offx = row_ref[0]
                offy = row_ref[1]
            axis_list[-1].append((axis_list[row-1][col][0] - offx,
                              axis_list[row-1][col][1] - offy))


    if col > 0:

        file_1 = os.path.join(path, name_generator(row, col-1))
        file_2= os.path.join(path, file)
        offx, offy = estimate_offset(file_1, file_2)
        if abs(offx - col_ref[0]) + abs(offy - col_ref[1]) < 20:
            axis_list[-1].append((axis_list[row][col-1][0] - offx,
                                  axis_list[row][col-1][1] - offy))
        else:
            if row > 0:
                file_1 = os.path.join(path, name_generator(row-1, col))
                file_2= os.path.join(path, file)
                offx, offy = estimate_offset(file_1, file_2)
                if abs(offx - row_ref[0]) + abs(offy - row_ref[1]) < 20:
                    axis_list[-1].append((axis_list[row-1][col][0] - offx,
                                      axis_list[row-1][col][1] - offy))
                else:
                    axis_list[-1].append((axis_list[row][col-1][0] - col_ref[0],
                                          axis_list[row][col-1][1] - col_ref[1]))
            else:
                axis_list[-1].append((axis_list[row][col-1][0] - col_ref[0],
                                      axis_list[row][col-1][1] - col_ref[1]))



        






        



for i, row in enumerate(axis_list):
    for j, cell in enumerate(row):
        axis_list[i][j] = (int(axis_list[i][j][0]), int(axis_list [i][j][1]))

min_x , min_y, max_x, max_y = 0, 0, 0, 0
for row in axis_list:
    for cell in row:
        max_x = max(max_x, cell[0])
        max_y = max(max_y, cell[1])
        min_x = min(min_x, cell[0])
        min_y = min(min_y, cell[1])
for i, row in enumerate(axis_list):
    for j, cell in enumerate(row):
        axis_list[i][j] = (cell[0] - min_x, cell[1] - min_y)
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
for file in file_list:
    name_part = file.split('.')[0]
    row = int(name_part.split('_')[0])
    col = int(name_part.split('_')[1])

    img = cv2.imread(os.path.join(path, file))
    if img is None:
        print(f"Cannot read")
        continue  # skip missing image
    img_f = img.astype(np.float32)
    illum = cv2.GaussianBlur(img_f, (101, 101), 0)
    illum_mean = np.mean(illum, axis=(0,1), keepdims=True)

    img_corrected = img_f / (illum / (illum_mean + 1e-6))

    img = np.clip(img_corrected, 0, 255).astype(np.uint8)
    x, y = axis_list[row][col]
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


cv2.imwrite("mosaic_image2.jpg", mosaic)

