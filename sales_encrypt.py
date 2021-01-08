import os
import shutil
import sys
import glob
import git


CUR_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
ROOT = os.path.dirname(CUR_DIR)
SRC_DIR = os.path.join(ROOT, 'sales')
DST_DIR = os.path.join(ROOT, 'sales-encrypt')



def main():
    if not os.path.exists(SRC_DIR):
        print('sales does not exists')
        return

    lst_cache = []
    lst_encrypt = []
    for d in os.listdir(SRC_DIR):
        if d in ('.git', '.gitignore', '.idea', 'data', 'log', 'media', 'static', 'templates', 'sales', 'utils'):
            continue
        src_dir = os.path.join(SRC_DIR, d)
        if os.path.isfile(src_dir):
            continue
        # フォルダーの場合
        if os.path.exists(os.path.join(src_dir, '__pycache__')):
            lst_cache.append("rm -rf {}/{}".format(d, '__pycache__'))
        files = glob.iglob(os.path.join(src_dir, "*.py"))
        for file in files:
            name = os.path.basename(file)
            # if name == "__init__.py":
            #     continue
            command = "sourcedefender encrypt --ttl=10000d --remove {}/{}".format(d, name)
            lst_encrypt.append(command)
    for i in lst_cache:
        print(i)
    for i in lst_encrypt:
        print(i)


def copy_changed_files():
    repo = git.Repo(SRC_DIR)
    diff_files = repo.git.diff(name_only=True).splitlines()
    for f in diff_files:
        name, ext = os.path.splitext(f)
        if ext != '.py':
            continue
        dst_file = os.path.join(DST_DIR, f)
        pye_file = dst_file + 'e'
        if os.path.exists(pye_file):
            os.remove(pye_file)
        src_file = os.path.join(SRC_DIR, f)
        if not os.path.exists(src_file):
            print('ファイルが見つからない', f)
            return
        shutil.copyfile(src_file, dst_file)
        dir_name = os.path.basename(os.path.dirname(dst_file))
        if dir_name in ('utils'):
            continue
        print("sourcedefender encrypt --ttl=10000d --remove {}".format(f))


if __name__ == '__main__':
    main()
