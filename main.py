import os
import shutil
import sys
import tkinter as tk
from tkinter import filedialog


def extract_relative_path(full_path):
    drive, tail = os.path.splitdrive(full_path)
    return os.path.relpath(tail, os.environ['USERPROFILE'])


def copy_directory_structure(source_rel_path, target_base_path):
    source_full_path = os.path.join(os.environ['USERPROFILE'], source_rel_path)
    target_full_path = os.path.join(target_base_path, source_rel_path)
    os.makedirs(target_full_path, exist_ok=True)
    shutil.copytree(source_full_path, target_full_path, dirs_exist_ok=True)


def create_copy_batch_file(src_folder, dst_folder, batch_file_path):
    with open(batch_file_path, 'w') as f:
        f.write(f'@echo off\n')
        f.write(f'robocopy "{src_folder}" "{dst_folder}" /MIR\n')


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
            # 清空输入框
            source_path_entry.delete(0, tk.END)
            target_path_entry.delete(0, tk.END)

            # 执行复制和批处理文件创建逻辑
            rel_path = extract_relative_path(source_path)
            copy_directory_structure(rel_path, target_path)
            batch_file_path = os.path.join(target_path, 'copy_to_user_profile.bat')
            create_copy_batch_file(os.path.join(target_path, rel_path),
                                   os.path.join(os.environ['USERPROFILE'], rel_path),
                                   batch_file_path)

            # 显示成功消息
            result_label.config(text="Script executed successfully.")
            root.update_idletasks()  # 更新GUI显示

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
