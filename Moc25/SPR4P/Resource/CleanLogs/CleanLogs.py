import os
import sys
from pathlib import Path


log_path = r"C:\daily"


def get_sut_path():
    sut_folders = Path(log_path).glob("*")
    return sut_folders


def get_test_path(sut_path):
    test_folders = Path(sut_path).glob("*")
    return test_folders


def get_test_files(test_path):
    test_files = Path(test_path).glob("*")
    return list(test_files)


def delete(path):
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            file_name = Path(root)/name
            os.chmod(file_name, 0o777)
            os.remove(file_name)  # 删除文件
        for name in dirs:
            path_name = Path(root)/name
            os.rmdir(path_name)  # 删除一个空目录
    os.rmdir(path)


if __name__ == '__main__':
    clean_count_less = 10
    args = sys.argv
    if len(args) > 1:
        clean_count_less = int(args[1]) if args[1].isdigit() else clean_count_less
    for sut_path in get_sut_path():
        for test_path in get_test_path(sut_path):
            files = get_test_files(test_path)
            if len(files) < clean_count_less:
                print(f"Remove folder: {test_path}")
                delete(test_path)
