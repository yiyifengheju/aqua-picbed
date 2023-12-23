import os

path = r'H:\RAF_TMP'
# path = r'H:\test'

for folder in os.listdir(path):
    files = os.listdir(os.path.join(path, folder))
    for file in files:
        os.rename(f'{path}/{folder}/{file}',
                  f'{path}/{folder}/{file[:-4]}')
