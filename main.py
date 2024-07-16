import os
import shutil
import sys
import tkinter as tk
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from tkinter import filedialog

import logging
# 确保log目录存在
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log')
os.makedirs(log_dir, exist_ok=True)

# 动态生成日志文件名，包含日期
now = datetime.now()
log_file_path = os.path.join(log_dir, f'{now.strftime("%Y-%m-%d")}.log')

# 创建一个logger
logger = logging.getLogger("GLOBAL")
logger.setLevel(logging.ERROR)  # 设置logger级别

# 定义日志格式
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# 创建并添加FileHandler
file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# 创建并添加StreamHandler（输出到控制台）
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def extract_relative_path(full_path):
    drive, tail = os.path.splitdrive(full_path)
    try:
        return os.path.relpath(tail, os.environ['USERPROFILE'])
    except ValueError as e:
        logging.error(f"Error calculating relative path: {e}")
        raise


def copy_directory_structure(source_rel_path, target_base_path):
    source_full_path = os.path.join(os.environ['USERPROFILE'], source_rel_path)
    target_full_path = os.path.join(target_base_path, source_rel_path)
    try:
        os.makedirs(target_full_path, exist_ok=True)
        shutil.copytree(source_full_path, target_full_path, dirs_exist_ok=True)
    except shutil.Error as e:
        logging.error(f"Error copying directory structure: {e}")
        raise
    except OSError as e:
        logging.error(f"OS error during copy operation: {e}")
        raise


def create_copy_batch_file(src_folder, dst_folder, batch_file_path):
    try:
        # 直接在批处理文件中使用宏，不解析完整路径
        src_folder_macro = '.\\appdata'  # .. 表示上级目录，但在这里是同级目录
        dst_folder_macro = '%UserProfile%\\appdata'

        batch_file_content = f'''@echo off
        rem Use relative path
        set "SRC={src_folder_macro}"

        rem Target directory uses environment variables
        set "DST={dst_folder_macro}"

        robocopy "%SRC%" "%DST%" /E /R:100000 /W:30

        '''

        with open(batch_file_path, 'w', encoding='cp1252') as f:
            f.write(batch_file_content)
    except IOError as e:
        logging.error(f"IO error creating batch file: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error creating batch file: {e}")
        raise


def get_paths(root):
    def on_browse_source():
        source_path = filedialog.askdirectory(title="Select Source Directory")
        source_path_entry.delete(0, tk.END)
        source_path_entry.insert(0, source_path)

    def on_browse_target():
        target_path = filedialog.askdirectory(title="Select Target Directory")
        target_path_entry.delete(0, tk.END)
        target_path_entry.insert(0, target_path)

    def on_ok():
        source_path = source_path_entry.get()
        target_path = target_path_entry.get()
        if source_path and target_path:
            try:
                # 改变当前工作目录为 source_path
                os.chdir(source_path)

                # 清空输入框
                source_path_entry.delete(0, tk.END)
                target_path_entry.delete(0, tk.END)

                # 执行复制和批处理文件创建逻辑
                rel_path = extract_relative_path(source_path)
                print(rel_path)
                copy_directory_structure(rel_path, target_path)
                batch_file_path = os.path.join(target_path, 'copy_to_user_profile.bat')
                create_copy_batch_file(os.path.join(target_path, rel_path),
                                       os.path.join(os.environ['USERPROFILE'], rel_path),
                                       batch_file_path)

                # 显示成功消息
                result_label.config(text="Script executed successfully.")
                root.update_idletasks()  # 更新GUI显示
            except Exception as e:
                result_label.config(text=f"An error occurred: {str(e)}")
                root.update_idletasks()

    # GUI elements
    source_label = tk.Label(root, text="Source Directory:")
    source_label.pack()

    source_path_entry = tk.Entry(root, width=50)
    source_path_entry.pack()

    source_browse_button = tk.Button(root, text="Browse", command=on_browse_source)
    source_browse_button.pack()

    target_label = tk.Label(root, text="Target Directory:")
    target_label.pack()

    target_path_entry = tk.Entry(root, width=50)
    target_path_entry.pack()

    target_browse_button = tk.Button(root, text="Browse", command=on_browse_target)
    target_browse_button.pack()

    ok_button = tk.Button(root, text="OK", command=on_ok)
    ok_button.pack(side=tk.LEFT)

    cancel_button = tk.Button(root, text="Cancel", command=root.quit)
    cancel_button.pack(side=tk.RIGHT)

    result_label = tk.Label(root, text="", fg="green")  # 添加一个标签来显示结果
    result_label.pack()

    root.mainloop()


if __name__ == '__main__':
    root = tk.Tk()
    root.title("Path Selection")

    get_paths(root)
