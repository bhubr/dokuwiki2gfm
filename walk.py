import os

data_path = '/Users/benoit/Documents/dokuwiki/data'
pages_path = os.path.join(data_path, 'pages')
meta_path = os.path.join(data_path, 'meta')

path_len = len(data_path)

files = []
# r=root, d=directories, f = files
for r, d, f in os.walk(pages_path):
    for file in f:
        file_abspath = os.path.join(r, file)
        # File name relative to pages path
        file_relative = file_abspath[path_len+1:]
        # Relative file name without extension
        file_base = os.path.splitext(file_relative)[0]
        print('SCANNING ' + file_base)
        for rr, dd, ff in os.walk(meta_path + '/' + file_base):
            for ffile in ff:
                print(file_base, ffile)
        files.append(file_abspath)

for f in files:
    print(f)
