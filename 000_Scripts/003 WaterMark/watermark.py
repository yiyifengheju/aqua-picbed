# -*- coding: utf-8 -*-
"""
====================================
@File Name ：003 WaterMark.py
@Time ： 2022/7/15 17:02
@Program IDE ：PyCharm
@Create by Author ： 一一风和橘
@Motto ：'The trick, William Potter, is not minding that it hurts.'
@About : 
====================================
"""
import glob
import os
import threading

import exifread
from PIL import Image, ImageDraw, ImageFont


def get_exif(path):
    """
    相机厂商：tags[Image Make]
    相机型号：tags[Image Model]
    镜头型号：tags[EXIF LensModel]
    拍摄时间：tags[Image DateTime]
    作者：tags[Image Artist]

    等效焦距：tags[EXIF FocalLengthIn35mmFilm]
    曝光时间：tags[EXIF ExposureTime]
    光圈大小：tags[EXIF FNumber]
    ISO：tags[EXIF ISOSpeedRatings]
    """
    f = open(path, 'rb')
    tags = exifread.process_file(f)
    f.close()
    return tags


def my_border(img, loc='b', width=100, color=(255, 255, 255)):
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


def generate_image(file_path, webp_path):
    # 打开图片
    img = Image.open(file_path).convert('RGBA')

    # 获取EXIF
    tags = get_exif(file_path)

    # 调整大小
    w = 2160
    h = int(w * img.size[1] / img.size[0])
    img = img.resize((w, h))

    # 添加白边
    image_border = my_border(img, width=200)
    # image_border.show()

    # 添加文字
    draw = ImageDraw.Draw(image_border)
    font = ImageFont.FreeTypeFont(font='C:/Users/MasterMao/AppData/Local/Microsoft/Windows/Fonts/Lato Italic.ttf',
                                  size=80)
    draw.text(xy=(100, h + 50), text=str(tags['Image Model']), fill=(0, 0, 0), font=font)

    draw.line([(int(w * 0.5 + 430), int(h + 55)), (int(w * 0.5 + 430), int(h + 140))], width=3,
              fill='black')

    font = ImageFont.FreeTypeFont(font='C:/Users/MasterMao/AppData/Local/Microsoft/Windows/Fonts/Lato Italic.ttf',
                                  size=45)
    text = f'{tags["EXIF FocalLengthIn35mmFilm"]}mm  ' \
           f'f/{tags["EXIF FNumber"]}  ' \
           f'{tags["EXIF ExposureTime"]}  ' \
           f'ISO{tags["EXIF ISOSpeedRatings"]}'
    draw.text(xy=(0.5 * w + 450, h + 45), text=text, fill=(0, 0, 0), font=font)

    font = ImageFont.FreeTypeFont(font='C:/Users/MasterMao/AppData/Local/Microsoft/Windows/Fonts/Lato Italic.ttf',
                                  size=35)
    text = f'{tags["EXIF LensModel"]}'
    draw.text(xy=(0.5 * w + 450, h + 105), text=text, fill=(0, 0, 0), font=font)

    # 添加图片
    logo = Image.open('Logo/logo.png').convert('RGBA').resize((452, 80))
    image_border.paste(logo, (int(w * 0.5 - 40), int(h + 60)))
    # image_border.show()

    # 保存路径
    file_name = os.path.split(file_path)[-1] + '.webp'
    file_path = os.path.join(webp_path, file_name)
    # image_border = image_border.convert('RGB')
    image_border.save(file_path, "WEBP")


def run():
    path = 'ImgInit'
    webp_path = os.path.dirname(os.path.abspath(__file__)) + "\img_webp"
    if not os.path.exists(webp_path):
        os.makedirs(webp_path)
    for file_path in glob.glob(f"{path}/*.[jp][pn]g"):
        t = threading.Thread(target=generate_image, args=(file_path, webp_path,))
        t.start()
        t.join()





if __name__ == "__main__":
    run()
