import gzip
import os
import pathlib
import re
import subprocess

default_author = 'laurent'
doku_path = '/Users/benoit/Documents/dokuwiki'
data_path = os.path.join(doku_path, 'data')
pages_path = os.path.join(data_path, 'pages')
meta_path = os.path.join(data_path, 'meta')
rev_path = os.path.join(data_path, 'attic')
 
path_len = len(data_path)
changes_dict = {}
authors_dict = {}
replacements_dict = {
    "start.txt": "Home.md"
}
try:
    users_file = os.path.join(doku_path, 'conf/users.auth.php')
    fa = open(users_file)
    author_lines = fa.read().split('\n')
    authors = list(filter(lambda x: re.match(r"[a-z]+:.*", x), author_lines))
    print(authors)
    exit
    for l in authors:
        lb = l.split(':')
        username = lb[0]
        fullname = lb[2]
        email = lb[3]
        authors_dict[username] = (fullname, email) 
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
    with gzip.open(input_fullpath, 'r') as f:
        doku_bytes= f.read()
        doku_content = doku_bytes.decode()
        # print('content: [' + doku_content.decode() + ']')
        # print(type(doku_content))
    repo_path = os.path.join(os.getcwd(), 'testrepo')

    output_fullpath = os.path.join(repo_path, output_file)

    output_dir = os.path.dirname(output_fullpath)
    pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)

    pandoc_args = ['pandoc', '-f', 'dokuwiki', '-t', 'gfm', '-o', output_fullpath]
    pandoc_call = subprocess.run(pandoc_args, stdout=subprocess.PIPE, text=True, input=doku_content)

    git_add_call = subprocess.run(['git', 'add', output_file], cwd=repo_path)

#    name_email = re.findall(r"(.*) <([^>]*)>", identity)
    name, email = identity

    git_env = os.environ.copy()
    git_env['GIT_COMMITTER_NAME'] = name
    git_env['GIT_AUTHOR_NAME'] = name
    git_env['GIT_COMMITTER_EMAIL'] = email
    git_env['GIT_AUTHOR_EMAIL'] = email
    git_commit_args = ['git', 'commit', '-m', msg, '--date', timestamp]
    git_commit_call = subprocess.run(git_commit_args, cwd=repo_path, env=git_env)

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
        if not author_identity:
            author_identity = authors_dict.get(default_author)
        name, email = author_identity
        print(sf, orig_file, ts, author_identity, commit_msg)

        output_file = replacements_dict.get(orig_file)
        if not output_file:
            output_file = orig_file.replace('.txt', '.md')

        doku_to_gfm(sf, output_file, ts, author_identity, commit_msg)
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
