import os
def find_files(folder_path):
    """
    遍历指定文件夹，找出所有.mp3文件并打印其名称。
    参数:
        folder_path (str): 要遍历的文件夹路径。
    """
    # 使用 os.walk 遍历文件夹及其所有子文件夹
    for root, dirs, files in os.walk(folder_path):
        # root: 当前目录路径
        # files: 当前目录下的文件名列表
        for file in files:
            # 检查文件扩展名是否为 .mp3 (不区分大小写)
            if file.lower().endswith('.mp3'):
                # 打印文件的完整路径，或只打印文件名
                full_path = os.path.join(root, file)
                print(full_path)  # 或者只打印 print(file)


# 示例：遍历当前目录下的 'music' 文件夹
if __name__ == "__main__":
    target_folder = "D:\FFOutput"  # 请将此路径替换为你要遍历的实际文件夹路径
    if os.path.exists(target_folder):
        find_files(target_folder)
    else:
        print(f"错误：文件夹 '{target_folder}' 不存在。")