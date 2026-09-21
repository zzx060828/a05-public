#生成mp3文件并播放
import asyncio
import edge_tts
import pygame
import time

async def generate_and_play_audio():
    # 配置参数
    text = "你好，要一碗肠粉"
    #text = "Hello World, welcome to the world of Edge-TTS!"
    voice = "zh-HK-HiuGaaiNeural"  # 语音可以修改
    output_file = "output.mp3"

    # 创建通信对象
    communicate = edge_tts.Communicate(text=text,
                                       voice=voice,
                                       rate="+0%",  # 语速，+10%表示加快10%，-10%表示减慢10%
                                       pitch="+0Hz") # 音调

    # 生成并保存音频
    await communicate.save(output_file)
    print(f"✅ 音频文件已保存: {output_file}")

    pygame.mixer.init()
    print("正在加载音频...")
    pygame.mixer.music.load(output_file)
    print("正在播放...")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.01)
    print("播放完成...")
    pygame.mixer.quit()
    # 返回文件路径供后续播放
    return output_file


# 运行
if __name__ == "__main__":
    audio_file = asyncio.run(generate_and_play_audio())


'''{
        "美式英语 (女)": "en-US-JennyNeural",
        "美式英语 (男)": "en-US-GuyNeural",
        "英式英语 (女)": "en-GB-SoniaNeural",
        "英式英语 (男)": "en-GB-RyanNeural",
        "中文普通话 (女)": "zh-CN-XiaoxiaoNeural",
        "中文普通话 (男)": "zh-CN-YunxiNeural",
        "粤语 (女)": "zh-HK-HiuGaaiNeural",
        "日语 (女)": "ja-JP-NanamiNeural",
        "韩语 (女)": "ko-KR-SunHiNeural",
    }'''