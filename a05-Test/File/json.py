import json

def read_json_file(file_path):
    """
    读取JSON文件并解析为Python对象
    """
    try:
        # 打开文件
        with open(file_path, 'r', encoding='utf-8') as file:
            # 使用json.load()从文件对象读取并解析
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"文件 {file_path} 不存在")
        return None
    except json.JSONDecodeError:
        print(f"JSON 解析错误: 文件 {file_path} 格式不正确")
        return None
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
        return None

# 使用示例
json_data = read_json_file('example.json')
if json_data:
    print("JSON数据:", json_data)
    print("数据类型:", type(json_data))  # 通常是dict或list