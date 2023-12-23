# -*- coding: utf-8 -*-
"""
====================================
@File Name ：test.py
@Time ： 2022/7/24 17:10
@Program IDE ：PyCharm
@Create by Author ： 一一风和橘
@Motto："The trick, William Potter, is not minding that it hurts."
====================================
"""
# import exifread
#
# path = './ImgInit/DSCF0540.jpg'
# f = open(path, 'rb')
# tags = exifread.process_file(f)
# for item in tags:
#     print(item, tags[item])

import threading
from time import sleep


def threading_1():
    sleep(3)
    print('子线程1结束')


def threading_2():
    sleep(10)
    print('子线程2结束')


if __name__ == '__main__':
    threads = []
    t1 = threading.Thread(target=threading_1)
    threads.append(t1)
    t1.start()

    t2 = threading.Thread(target=threading_2, daemon=True)
    threads.append(t2)
    t2.start()

    [thread.join(5) for thread in threads]

    sleep(1)
    print('主线程结束')

self.max_threads_num = 8

self.pool_sema = threading.BoundedSemaphore(value=self.max_threads_num)
