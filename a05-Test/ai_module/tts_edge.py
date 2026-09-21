# 文件名：tts_edge.py
import edge_tts
import os
import uuid
import asyncio
import logging

logger = logging.getLogger(__name__)

# 主语音 + 备用语音池（按优先级排列）
VOICE_POOL = [
    "zh-CN-YunxiNeural",      # 主：男声
    "zh-CN-XiaoxiaoNeural",   # 备用1：女声
    "zh-CN-YunyangNeural",    # 备用2：男声新闻风
]


async def _try_generate(text: str, voice: str, output_path: str) -> bool:
    """单次尝试，成功返回 True，失败返回 False"""
    try:
        communicate = edge_tts.Communicate(text=text, voice=voice, rate="+15%")
        await communicate.save(output_path)
        return True
    except Exception as e:
        logger.warning(f"TTS 尝试失败 (voice={voice}): {e}")
        return False


async def text_to_speech(text: str, session_id: str) -> str:
    text = text.strip()
    if not text:
        raise ValueError("TTS 输入文本为空")

    audio_dir = "static/audio"
    os.makedirs(audio_dir, exist_ok=True)

    output_filename = f"reply_{session_id}_{uuid.uuid4().hex[:6]}.mp3"
    output_path = os.path.join(audio_dir, output_filename)

    # 遍历语音池 + 重试
    last_error = None
    for voice in VOICE_POOL:
        for attempt in range(2):
            if await _try_generate(text, voice, output_path):
                logger.info(f"TTS 成功: voice={voice}, attempt={attempt + 1}")
                return output_path
            await asyncio.sleep(1.5)

    # 所有尝试均失败
    raise RuntimeError(
        f"Edge TTS 全部 {len(VOICE_POOL)} 个语音各重试2次后仍失败，微软服务当前不可用"
    )