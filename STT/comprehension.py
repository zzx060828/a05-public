"""STT通过ASR实现"""
import os
import time
from urllib.parse import urlencode
from dotenv import load_dotenv
import requests

# 加载环境变量（从项目的.env文件）
load_dotenv()


class AliYunASR:
    """阿里云语音识别服务封装类"""
    def __init__(self):
        # 从环境变量读取阿里云配置

        self.access_key_id = os.getenv('ALIYUN_ACCESS_KEY_ID')
        self.access_key_secret = os.getenv('ALIYUN_ACCESS_KEY_SECRET')
        self.app_key = os.getenv('ALIYUN_ASR_APP_KEY')
        self.region_id = os.getenv('ALIYUN_REGION_ID', 'cn-shanghai')
        self.api_version = '2019-02-28'

        # 检查配置是否完整
        if not all([self.access_key_id, self.access_key_secret, self.app_key]):
            print("警告：阿里云ASR配置不完整，请检查.env文件")
            print(f"AccessKey ID: {'已设置' if self.access_key_id else '未设置'}")
            print(f"AccessKey Secret: {'已设置' if self.access_key_secret else '未设置'}")
            print(f"AppKey: {'已设置' if self.app_key else '未设置'}")

        # 初始化HTTP客户端（简化版本，实际使用可能需要requests库）
        self._init_client()

    def get_token(self):
        """
        创建阿里云语音识别Token请求的通用方法
        """
        from aliyunsdkcore.client import AcsClient
        from aliyunsdkcore.request import CommonRequest

        client = AcsClient(self.access_key_id, self.access_key_secret, self.region_id)

        request = CommonRequest()
        request.set_domain('nls-meta.cn-shanghai.aliyuncs.com')
        request.set_version('2019-02-28')
        request.set_action_name('CreateToken')
        request.set_protocol_type('https')
        try:
            response = client.do_action_with_exception(request)
            print(str(response, encoding='utf-8'))
            # 解析返回的JSON字符串
            import json
            token_info = json.loads(response.decode('utf-8'))
            self.token = token_info.get('Token', {}).get('Id')
            return self.token
        except Exception as e:
            print(f"获取Token失败: {e}")
            return None


    def _init_client(self):
        """初始化HTTP客户端"""
        try:
            # 这里使用requests库进行HTTP调用
            import requests
            self.requests = requests
            self.session = requests.Session()
            print("HTTP客户端初始化成功")
        except ImportError:
            print("请安装requests库: pip install requests")
            self.requests = None


    def transcribe_file(self, audio_file_path: str) -> str:
        """
        识别音频文件为文字
        """
        if not os.path.exists(audio_file_path):
            return "[识别失败]：音频文件不存在"

        if not self.requests:
            return "[识别失败]：requests库未安装，请执行 pip install requests"

        # 1. 获取访问令牌
        token = self.get_token()
        if not token:
            return "[识别失败]：无法获取阿里云访问令牌，请检查AccessKey配置"

        # 2. 读取音频文件
        try:
            with open(audio_file_path, 'rb') as audio_file:
                audio_data = audio_file.read()
                #audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        except Exception as e:
            return f"[识别失败]：无法读取音频文件 - {str(e)}"

        # 3. 构建识别请求
        # 阿里云一句话识别API端点（同步）
        recognize_url = f"https://nls-gateway.{self.region_id}.aliyuncs.com/stream/v1/asr"

        # 构建请求参数
        params = {
            'appkey': self.app_key,
            'format': 'wav',  # 根据实际格式调整
            'sample_rate': 16000,
            'enable_punctuation_prediction': True,
            'enable_inverse_text_normalization': True,
        }

        # 构建请求头
        headers = {
            'X-NLS-Token': token,
            'Content-Type': 'application/octet-stream',
            'Content-Length': str(len(audio_data))
        }

        # 4. 发送请求
        try:
            response = requests.post(
                f"{recognize_url}?{urlencode(params)}",
                headers=headers,
                data=audio_data,
                timeout=30
            )

            print(f"🔍 ASR请求状态码: {response.status_code}")
            print(f"🔍 ASR响应内容: {response.text}")

            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 20000000:
                    text = result.get('result', '')
                    return text if text else "[识别失败]：识别结果为空"
                else:
                    return f"[识别失败]：{result.get('message', '识别失败')}"
            else:
                return f"[识别失败]：HTTP错误 {response.status_code}"

        except Exception as e:
            return f"[识别失败]：请求异常 - {str(e)}"

    # 更新您的 speech_to_text 函数
def speech_to_text(audio_file_path: str) -> str:
    asr = AliYunASR()
    return asr.transcribe_file(audio_file_path)


# ============================================================================
# 测试函数
# ============================================================================

def test_speech_to_text():
    """测试语音识别功能"""
    print("=" * 60)
    print("测试 speech_to_text 函数")
    print("=" * 60)

    # 测试用例1：使用示例音频文件（需要准备）
    test_audio = input("请输入测试音频文件路径（留空使用默认）: ").strip()

    if not test_audio:
        # 如果没有提供，使用默认测试文件
        default_audio = "test_audio.wav"
        if os.path.exists(default_audio):
            test_audio = default_audio
        else:
            print("没有找到测试音频文件，请手动指定")
            return

    if not os.path.exists(test_audio):
        print(f"文件不存在: {test_audio}")
        return

    # 执行识别
    print(f"\n处理文件: {test_audio}")
    result = speech_to_text(test_audio)

    # 显示结果
    print(f"\n识别结果: {result}")

    # 评估结果
    if result == "[识别失败]":
        print("识别失败，请检查配置和网络")
    elif "识别失败" in result:
        print(f"识别失败: {result}")
    else:
        print("识别成功！")
        print(f"识别内容: {result}")

        # 保存结果到文件
        result_file = "transcription_result.txt"
        with open(result_file, "w", encoding="utf-8") as f:
            f.write(f"音频文件: {test_audio}\n")
            f.write(f"识别时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"识别结果:\n{result}\n")
        print(f"结果已保存至: {result_file}")
if __name__ == "__main__":
    # 当直接运行这个文件时，执行测试
    test_speech_to_text()

