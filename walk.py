import os
import re

data_path = '/Users/benoit/Documents/dokuwiki/data'
pages_path = os.path.join(data_path, 'pages')
meta_path = os.path.join(data_path, 'meta')
rev_path = os.path.join(data_path, 'attic')
 
path_len = len(data_path)

def is_revision(filename):
    return re.match(r".*\d+\.txt\.gz", filename)

def get_revisions():
    files = []
    for r, d, f in os.walk(rev_path):
        for file in f:
            file_abspath = os.path.join(r, file)
            if is_revision(file_abspath):
                files.append(file_abspath)
    sorted_files = sorted(files, key=lambda k: k.split('.')[-3:-2])
    print('\n'.join(sorted_files))

def get_pages():
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

get_revisions()
