# -*- coding: utf-8 -*-
"""
====================================
@File Name ：WaterMarkClass.py
@Time ： 2022/7/24 15:32
@Program IDE ：PyCharm
@Create by Author ： 一一风和橘
@Motto："The trick, William Potter, is not minding that it hurts."
====================================
"""
import glob
import os
import threading

import exifread
import tqdm
from PIL import Image, ImageDraw, ImageFont

QUALITY_INIT = 100
AIM_SIZE = 500
COMPRESS_RATE = []

CAMERA_MAKE = 'fujifilm'

INIT_PATH = './ImgInit'
WEBP_PATH = './ImgWebp'
AIM_WIDTH = 2560
BORDER_WIDTH = 150
FONT_PATH = 'C:/Users/MasterMao/AppData/Local/Microsoft/Windows/Fonts/Lato-Italic.ttf'


class WaterMarkClass:
    def __init__(self, max_threads_num=8):
        self.init_path = INIT_PATH
        self.webp_path = WEBP_PATH
        self.border_width = BORDER_WIDTH
        self.width = AIM_WIDTH
        self.font = FONT_PATH
        self.camera_make = CAMERA_MAKE.lower()
        self.logo = f'./Logo/{CAMERA_MAKE}.png'
        self.pool_sema = threading.BoundedSemaphore(value=max_threads_num)

    def check(self):
        if not os.path.exists(self.webp_path):
            os.makedirs(self.webp_path)
        assert os.path.exists(self.font), f'{os.path.split(self.font)[-1]}字体不存在！'
        return True

    def run(self):
        self.check()
        all_image_path = tqdm.tqdm(glob.glob(f"{self.init_path}/*.[jp][pn]g"))
        threads = []
        for file in all_image_path:
            thread_name = os.path.split(file)[-1]
            t = threading.Thread(target=self.generate_image, args=(file,), name=thread_name)
            threads.append(t)
            all_image_path.set_description(f'添加进程{thread_name}')
            t.start()
        # print(f'共添加{threading.active_count()}个线程')

        t_threads = tqdm.tqdm(threads)
        for thread in t_threads:
            thread.join()
            num_threads = self.pool_sema.__dict__['_value']
            t_threads.set_description(f'正在转换{thread.name} 线程数：{8 - num_threads}')

    @staticmethod
    def get_exif(path):
        """获取图片的EXIF信息"""
        """
        相机厂商：tags['Image Make']
        相机型号：tags['Image Model']
        镜头型号：tags['EXIF LensModel']
        拍摄时间：tags['Image DateTime']
        作者：tags['Image Artist']

        等效焦距：tags['EXIF FocalLengthIn35mmFilm']
        曝光时间：tags['EXIF ExposureTime']
        光圈大小：tags['EXIF FNumber']
        ISO：tags['EXIF ISOSpeedRatings']
        """
        with open(path, 'rb') as f:
            tags = exifread.process_file(f)
        return tags

    @staticmethod
    def generate_border(img, loc='b', width=100, color=(255, 255, 255)):
        w = img.size[0]
        h = img.size[1]

        if loc in ['a', 'all']:
            w += 2 * width
            h += 2 * width
            img_new = Image.new('RGB', (w, h), color)
            img_new.paste(img, (width, width))
        elif loc in ['t', 'top']:
            h += width
            img_new = Image.new('RGB', (w, h), color)
            img_new.paste(img, (0, width, w, h))
        elif loc in ['r', 'right']:
            w += width
            img_new = Image.new('RGB', (w, h), color)
            img_new.paste(img, (0, 0, w - width, h))
        elif loc in ['b', 'bottom']:
            h += width
            img_new = Image.new('RGBA', (w, h), color)
            img_new.paste(img, (0, 0, w, h - width))
        elif loc in ['l', 'left']:
            w += width
            img_new = Image.new('RGB', (w, h), color)
            img_new.paste(img, (width, 0, w, h))
        else:
            img_new = img
        return img_new

    def generate_image(self, file_path):
        self.pool_sema.acquire()
        # 打开图片
        img = Image.open(file_path).convert('RGBA')
        old_size = os.path.getsize(file_path)
        filename = os.path.split(file_path)[-1].split('.')[0]
        # 获取图片信息
        tags = self.get_exif(file_path)
        # 调整大小
        height = int(self.width * img.size[1] / img.size[0])
        img = img.resize((self.width, height))

        # 添加白边
        image_border = self.generate_border(img, width=self.border_width)

        # 添加相机型号信息
        draw = ImageDraw.Draw(image_border)
        font = ImageFont.FreeTypeFont(font=self.font, size=80)
        if self.camera_make == 'sony':
            image_model = str(tags['Image Software']).split(' ')[0]
        elif self.camera_make == 'fujifilm':
            image_model = str(tags['Image Model'])
        else:
            image_model = ''
        assert image_model, '相机型号为空'
        draw.text(xy=(100, height + 25), text=image_model, fill=(0, 0, 0), font=font)
        # 添加竖线
        draw.line([(int(self.width * 0.5 + 430), int(height + 30)), (int(self.width * 0.5 + 430), int(height + 115))],
                  width=3, fill='black')
        # 添加图片信息
        # 等效焦距+光圈数+曝光时间+ISO
        font = ImageFont.FreeTypeFont(font=self.font, size=45)
        focal_length = tags["EXIF FocalLengthIn35mmFilm"]
        f_number = eval(str(tags["EXIF FNumber"]))
        exposure_time = tags["EXIF ExposureTime"]
        iso = tags["EXIF ISOSpeedRatings"]
        text = f'{focal_length}mm  ' \
               f'f/{f_number:.1f}  ' \
               f'{exposure_time}  ' \
               f'ISO{iso}'
        draw.text(xy=(0.5 * self.width + 450, height + 20), text=text, fill=(0, 0, 0), font=font)

        # 添加镜头信息
        font = ImageFont.FreeTypeFont(font=self.font, size=35)
        if self.camera_make == 'sony':
            lens_make = 'SONY'
        elif self.camera_make == 'fujifilm':
            lens_make = tags["EXIF LensMake"]
        else:
            lens_make = ''
        assert lens_make, '镜头型号为空'
        text = f'{lens_make}  {tags["EXIF LensModel"]}'
        draw.text(xy=(0.5 * self.width + 450, height + 80), text=text, fill=(0, 0, 0), font=font)

        # 添加相机品牌Logo
        logo = Image.open(self.logo).convert('RGBA').resize((452, 80))
        image_border.paste(logo, (int(self.width * 0.5 - 40), int(height + 35)))

        # 保存新图片并转为webp格式
        pre = tags['Image DateTime'].split(' ')[0].replace(':', '')
        file_name = pre + os.path.split(file_path)[-1] + '.webp'
        file_path = os.path.join(self.webp_path, file_name)
        # image_border = image_border.convert('RGB')
        new_size = old_size
        quality = QUALITY_INIT
        while new_size > AIM_SIZE * 1024:
            quality -= 2
            image_border.save(file_path, "WEBP", quality=quality)
            new_size = os.path.getsize(file_path)
        COMPRESS_RATE.append([filename, old_size / 1024, new_size / 1024, new_size / old_size])
        self.pool_sema.release()


if __name__ == '__main__':
    my_watermarker = WaterMarkClass(camera_make='fujifilm')
    my_watermarker.run()
