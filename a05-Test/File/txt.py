#r:读取 w：写  a:追加
def read_txt_file(file_path):
    """
    读取文本文件内容
    """
    try:
        # 打开文件，指定编码为utf-8
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()  # 读取全部内容
            return content
    except FileNotFoundError:
        print(f"文件 {file_path} 不存在")
        return None
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
        return None

# 使用示例
txt_content = read_txt_file('D:\大一上\PBLF\歌手信息.txt')
if txt_content:
    print("文本内容:\n",txt_content)