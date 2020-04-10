import os
import re
import subprocess

data_path = '/Users/benoit/Documents/dokuwiki/data'
pages_path = os.path.join(data_path, 'pages')
meta_path = os.path.join(data_path, 'meta')
rev_path = os.path.join(data_path, 'attic')
 
path_len = len(data_path)
changes_dict = {}
authors_dict = {}

try:
    fa = open('authors.txt')
    author_lines = fa.read().split('\n')
    authors = list(filter(lambda x: x != '', author_lines))
    for l in authors:
        lb = l.split(': ')
        username = lb[0]
        full_identity = lb[1]
        authors_dict[username] = full_identity
except:
    sys.exit("Could not find 'authors.txt'. Create it from the sample file")

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
    bits = change_line[0].split('\t')
    return (bits[0], bits[3], bits[4], bits[5])

def doku_to_gfm(input_file, output_file, timestamp, identity, msg):
    input_fullpath = os.path.join(rev_path, input_file)
    doku_content = ''
    with gzip.open(input_fullpath, 'rb') as f:
        doku_content = f.read()
    output_fullpath = os.path.join(os.getcwd, 'testrepo', output_file)
    pandoc_args = ['pandoc', '-f', 'dokuwiki', '-t', 'gfm', '-o', output_fullpath]
    pandoc_call = subprocess.run(pandoc_args, stdout=subprocess.PIPE, text=True, input=doku_content)

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
        changes_info = get_changes_info(sf)
        if not changes_info:
            print("WARNING! No info for " + sf)
            continue
        ts, action_l, username, msg = changes_info
        orig_file = re.sub(r'(.*)\.\d+\.txt\.gz', r'\1.txt', sf);
        action_verb = 'Creation ' if action_l == 'C' else 'MàJ '
        commit_msg = msg if msg else action_verb + orig_file
        author_identity = authors_dict.get(username)
        print(sf, orig_file, ts, author_identity, commit_msg)

        doku_to_gfm(sf, orig_file, ts, author_identity, commit_msg)
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
