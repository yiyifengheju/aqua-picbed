# -*- coding: utf-8 -*-
"""
====================================
@File Name: 002 auto_mkdocs.py
@Time: 2023/5/13 13:48
@Program IDE：PyCharm
@Create by Author: 一一风和橘
@Motto: "The trick, William Potter, is not minding that it hurts."
@Description:
- 
====================================
"""
import hashlib
import os
import random
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor

import exifread
import pandas as pd
import tqdm

PATH_INIT = r'C:\Users\MasterMao\Desktop\五月夏花'


class AutoMkdocs:
    def __init__(self):
        self.path_init = PATH_INIT
        self.path_save = r'H:\WEBP'
        self.limit_size = 800
        self.width_limit = 2560
        self.path_logo = 'https://cdn.jsdelivr.net/gh/yiyifengheju/picbed@main/sources/Fujifilm.svg'
        self.title = os.path.split(PATH_INIT)[-1]
        self.path_webp = self.get_webp_path()
        self.obj_list = []
        self.executor = ThreadPoolExecutor(max_workers=12)
        self.compress_res = []
        self.compress_rate_all = None
        self.html = ['---\n',
                     f'title: {self.title}\n',
                     f'comments: true\n',
                     f'hide:\n',
                     f'  - toc\n',
                     f'---\n\n',
                     f'<div class="photo-wall">\n']

    def run(self):
        # 第一步，压缩图片
        files = os.listdir(self.path_init)
        for item in files:
            obj = self.executor.submit(self.compress_image, item)
            self.obj_list.append(obj)

        # 第二步，停止接受新的任务，等待任务完成，统计结果
        self.executor.shutdown()
        for obj in self.obj_list:
            res = obj.result()
            self.compress_res.append(res)
        self.compress_res = pd.DataFrame(self.compress_res)
        self.compress_res.columns = ['Filename', '原始大小/kb', '压缩大小/kb', '压缩比']
        self.compress_rate_all = self.compress_res["压缩大小/kb"].mean() / self.compress_res["原始大小/kb"].mean()

        # 第三步，生成Markdown
        self.generate_md()
        with open(f'{self.path_save}/{self.path_webp}/{self.path_webp}.md', 'w', encoding='utf-8') as f:
            f.writelines(self.html)

    def get_webp_path(self):
        md5_hash = hashlib.md5()
        md5_hash.update(self.title.encode('utf-8'))
        path = rf'{self.path_save}\{md5_hash.hexdigest()[:8]}'
        if not os.path.exists(path):
            os.mkdir(path)
        else:
            shutil.rmtree(path)
            os.mkdir(path)
        return md5_hash.hexdigest()[:8]

    def compress_image(self, img_name):
        quality_init = 100
        aim_size = self.limit_size * 1024
        cmd = (f'cwebp -q {quality_init} {self.path_init}/{img_name} -o '
               f'{self.path_save}/{self.path_webp}/{img_name.split(".")[0]}.'
               f'webp -m 6 -size {aim_size} -resize {self.width_limit} 0 -noalpha -quiet -jpeg_like')
        process = subprocess.Popen(cmd, shell=True)
        process.wait()
        old_size = os.path.getsize(rf'{self.path_init}/{img_name}')
        new_size = os.path.getsize(rf'{self.path_save}/{self.path_webp}/{img_name.split(".")[0]}.webp')
        return img_name, old_size, new_size, new_size / old_size

    def generate_md(self):
        # 获取图片列表
        img_list = os.listdir(f'{self.path_save}/{self.path_webp}')
        random.shuffle(img_list)
        t_img_list = tqdm.tqdm(img_list)
        for img in t_img_list:
            if img[-2:] == 'md':
                continue
            t_img_list.set_description(f'{img}')

            # 读取文件EXIF信息
            path = f'{self.path_init}/{img[:-5]}.jpg'
            try:
                with open(path, 'rb') as f:
                    tags = exifread.process_file(f)
            except FileNotFoundError:
                continue

            camera_model = str(tags['Image Model'])
            focal_length = tags["EXIF FocalLengthIn35mmFilm"]
            f_number = eval(str(tags["EXIF FNumber"]))
            exposure_time = tags["EXIF ExposureTime"]
            iso = tags["EXIF ISOSpeedRatings"]

            lens_make = tags["EXIF LensMake"]
            lens_model = tags["EXIF LensModel"]

            # 生成图片html
            name = 's' + img.split(".")[0]
            tmp = f'<div class="photo"><img alt="{name}" class="thumb" ' \
                  f'data-description=".{name}" ' \
                  f'data-lazy-src="https://cdn.jsdelivr.net/gh/yiyifengheju/picbed@main/{self.path_webp}/{img}"></div>\n'
            self.html.append(tmp)

            # 生成水印html
            tmp = [f'<div class="glightbox-desc {name}">',
                   f'<div class="pre-msg">',
                   f'<div class="shot-model">{camera_model}</div>\n',
                   f'<div class="descript"></div> ',
                   f'</div>',
                   f'<div class="kong"></div>',
                   f'<div class="shot-logo"></div>',
                   f'<div class="vertical-line"></div>',
                   f'<div class="msg">',
                   f'<div class="lens-param">{focal_length}mm  f/{f_number:.1f}  {exposure_time}s  ISO{iso}</div>',
                   f'<div class="lens">{lens_make} {lens_model}</div>',
                   f'</div></div>', '\n\n']
            self.html.extend(tmp)
        self.html.append('</div>')


if __name__ == '__main__':
    am = AutoMkdocs()
    am.run()
