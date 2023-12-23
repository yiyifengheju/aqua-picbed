# -*- coding: utf-8 -*-
"""
=========================================================================
@File Name: compress.py
@Time: 2023/12/9 14:07
@Program IDE：PyCharm
@Create by Author: 一一风和橘
@Motto: "The trick, William Potter, is not minding that it hurts."
@Description:
- 
- 
=========================================================================
"""
import glob
import os
import threading

import pandas as pd
import tqdm
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()

PATH_INIT = r'C:\Users\MasterMao\Desktop\0622 端午礼物'
PATH_WEBP = r'C:\Users\MasterMao\Desktop\webp'

AIM_WIDTH = 2560
AIM_HEIGHT = 1280
QUALITY_INIT = 100
FORMAT = 'webp'
AIM_SIZE = 500


def create_image(file_path, save_path):
    filename = os.path.split(file_path)[-1].split('.')[0]
    old_size = os.path.getsize(file_path)
    new_size = old_size
    quality = QUALITY_INIT
    img = Image.open(file_path)
    w = img.size[0]
    h = img.size[1]

    height = int(AIM_WIDTH * h / w)
    img = img.resize((AIM_WIDTH, height))
    while new_size > AIM_SIZE * 1024:
        quality -= 5
        img.save(f"{save_path}/{filename}.{FORMAT}", f"{FORMAT}", quality=quality)
        new_size = os.path.getsize(f"{save_path}/{filename}.{FORMAT}")
    COMPRESS_RATE.append([filename, old_size / 1024, new_size / 1024, new_size / old_size])


def start(root_path, save_path):
    t_file_list = tqdm.tqdm(glob.glob(root_path + '/*.[jp][pn]g'))
    for infile in t_file_list:
        t = threading.Thread(target=create_image, args=(infile, save_path,))
        t.start()
        t.join()

    t_file_list = tqdm.tqdm(glob.glob(root_path + '/*.HEIC'))
    for infile in t_file_list:
        t = threading.Thread(target=create_image, args=(infile, save_path,))
        t.start()
        t.join()


if __name__ == "__main__":
    init_path = './ImgInit'
    webp_path = './ImgWebp'
    if not os.path.exists(webp_path):
        os.makedirs(webp_path)
    start(init_path, webp_path)
    print('转换完毕！')
    rate = pd.DataFrame(COMPRESS_RATE)
    rate.columns = ['文件名', '原始大小/kb', '压缩大小/kb', '压缩比']
    print(rate)
    print(f'总压缩比：{rate["压缩比"].mean()}')