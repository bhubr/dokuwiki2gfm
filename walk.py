import os
import re

data_path = '/Users/benoit/Documents/dokuwiki/data'
pages_path = os.path.join(data_path, 'pages')
meta_path = os.path.join(data_path, 'meta')
rev_path = os.path.join(data_path, 'attic')
 
path_len = len(data_path)
changes_dict = {}

def is_revision(filename):
    return re.match(r".*\d+\.txt\.gz", filename)

def get_changes_file(filename):
    content = changes_dict.get(filename)
    if not content:
        changes_file = os.path.join(meta_path, filename + '.changes')
        try:
            f = open(changes_file, 'r')
            # Do something with the file
            print('READ ' + changes_file)
            content = f.read()
            changes_dict[filename] = content
        except FileNotFoundError:
            print("File not accessible: " + changes_file)
#        finally:
#            f.close()
    return content


def get_changes_info(filename):
    segments = filename.split('.')
    base = segments[0]
    timestamp = segments[1]
    changes_content = get_changes_file(base)
    if not changes_content:
        return
    lines = changes_content.split('\n')
    change_line = list(filter(lambda l: timestamp in l, lines))
    print(change_line[0].split('\t'))

def get_revisions():
    files = []
    sub_index = len(rev_path) + 1
    for r, d, f in os.walk(rev_path):
        for file in f:
            file_abspath = os.path.join(r, file)
            file_relative = file_abspath[sub_index:]
            if is_revision(file_abspath):
                files.append(file_relative)
    sorted_files = sorted(files, key=lambda k: k.split('.')[-3:-2])
    for sf in sorted_files:
        file_base = sf.split('.')[0]
        get_changes_info(sf)
    # print('\n'.join(sorted_files))

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
