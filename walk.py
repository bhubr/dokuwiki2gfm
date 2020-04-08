import os

path = '/Users/benoit/Documents/dokuwiki/data/pages'
path_len = len(path)

files = []
# r=root, d=directories, f = files
for r, d, f in os.walk(path):
    for file in f:
        file_abspath = os.path.join(r, file)
        file_base = os.path.splitext(file)
        print(file_base)
        print(file_abspath[path_len+1:])
        files.append(file_abspath)

for f in files:
    print(f)
