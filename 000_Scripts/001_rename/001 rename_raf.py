# -*- coding: utf-8 -*-
"""
====================================
@File Name: 001 rename_raf.py
@Time: 2023/4/22 22:05
@Program IDE：PyCharm
@Create by Author: 一一风和橘
@Motto: "The trick, William Potter, is not minding that it hurts."
@Description:
- RAF文件重命名，时间+文件名
====================================
"""
import os
import shutil

import tqdm

PATH = r'C:\Users\MasterMao\Desktop\RAF'
NEW_PATH = r'H:\RAF_TMP'


def get_raf_date(raf_path):
    terminal_message = os.popen(rf'.\exiftool.exe {raf_path}').read()
    for line in terminal_message.split('\n'):
        if 'Date/Time Original' in line:
            return line.split(' : ')[-1].split(' ')[0].replace(':', '')
    assert 0, 'Find No Date/Time Original'


def get_raf_info(raf_path):
    res = {}
    terminal_message = os.popen(rf'.\exiftool.exe {raf_path}').read()
    for line in terminal_message.split('\n'):
        if line == '':
            continue
        if line[:6] == 'Scale':
            line = line.replace('t: ', 't : ')
        line = line.replace(' : ', '$')
        line = line.replace(':', '-')
        tmp = line.split('$')
        res[tmp[0].strip()] = tmp[1].strip()
    return res


def run():
    if not os.path.exists(NEW_PATH):
        os.mkdir(NEW_PATH)

    file_list = os.listdir(PATH)
    t_file_list = tqdm.tqdm(file_list)
    for file in t_file_list:
        if file == 'Desktop.ini':
            continue
        t_file_list.set_description(file)
        raf_path = os.path.abspath(f'{PATH}/{file}')
        # 获取原始时间
        pre = get_raf_date(raf_path)
        # 新建日期路径
        new_dir = f'{NEW_PATH}/{pre}'
        if not os.path.exists(new_dir):
            os.mkdir(new_dir)
        # 获取RAF信息
        # info = get_raf_info(raf_path)
        shutil.copy(f'{PATH}/{file}', f'{new_dir}/{pre}_{file.split(".")[0]}.RAF')


if __name__ == '__main__':
    run()
