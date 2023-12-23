# -*- coding: utf-8 -*-
"""
====================================
@File Name ：compress_cover.py
@Time ： 2023/3/17 0:00
@Program IDE ：PyCharm
@Create by Author ： 一一风和橘
@Motto ："The trick, William Potter, is not minding that it hurts."
@Description :
- 封面裁剪压缩
====================================
"""
import os
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import tqdm
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()

PATH_INIT = r'C:\Users\MasterMao\Desktop\0622 端午礼物'
PATH_WEBP = r'C:\Users\MasterMao\Desktop\webp'

AIM_WIDTH = 1920

QUALITY_INIT = 100
FORMAT = 'webp'
AIM_SIZE = 100


def cut_cover(file):
    filename = file.split('.')[0]
    filepath = f'{PATH_INIT}/{file}'
    old_size = os.path.getsize(filepath)
    new_size = old_size
    quality = QUALITY_INIT
    img = Image.open(filepath)
    w = img.size[0]
    h = img.size[1]

    height = int(AIM_WIDTH * h / w)
    img = img.resize((AIM_WIDTH, height))
    x0 = 0
    y0 = int(height / 3)
    x1 = AIM_WIDTH
    y1 = int(height / 3 * 2)
    img = img.crop((x0, y0, x1, y1))
    while new_size > AIM_SIZE * 1024:
        quality -= 5
        img.save(f"{PATH_WEBP}/{filename}.{FORMAT}", f"{FORMAT}", quality=quality)
        new_size = os.path.getsize(f"{PATH_WEBP}/{filename}.{FORMAT}")
    return [filename, old_size / 1024, new_size / 1024, new_size / old_size]


if __name__ == "__main__":
    if not os.path.exists(PATH_WEBP):
        os.makedirs(PATH_WEBP)
    compress_rate = []
    t_files = tqdm.tqdm(os.listdir(PATH_INIT))
    threads = ThreadPoolExecutor(max_workers=5)
    thread_list = []
    for file in t_files:
        t_files.set_description(f'{file}')
        obj = threads.submit(cut_cover, file)
        thread_list.append(obj)
    for future in thread_list:
        res = future.result()
        compress_rate.append(res)
    rate = pd.DataFrame(compress_rate)
    rate.columns = ['文件名', '原始大小/kb', '压缩大小/kb', '压缩比']
    print(rate)
    print(f'总压缩比：{rate["压缩大小/kb"].mean() / rate["原始大小/kb"].mean():.4f}')
