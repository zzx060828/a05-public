# 文件名：tts_edge.py
import edge_tts
import os
import uuid

async def text_to_speech(text: str, session_id: str) -> str:
    voice = "zh-CN-YunxiNeural" 
    
    # 在你的项目里建一个存放录音的文件夹
    audio_dir = "static/audio"
    os.makedirs(audio_dir, exist_ok=True)

    # 随机生成一个文件名，防止覆盖
    output_filename = f"reply_{session_id}_{uuid.uuid4().hex[:6]}.mp3"
    output_path = os.path.join(audio_dir, output_filename)

    # 生成音频并保存
    communicate = edge_tts.Communicate(text=text, voice=voice, rate="+15%")
    await communicate.save(output_path)
    
    # 只要生成成功，就把相对路径返回给 main.py
    return output_path