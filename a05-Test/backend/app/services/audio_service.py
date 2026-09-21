import ffmpeg
import logging
import uuid
import asyncio
import os
from pathlib import Path
from ..core.config import (
    AUDIO_UPLOAD_DIR,
    AUDIO_OUTPUT_DIR,
    AUDIO_BACKUP_DIR,
    FFMPEG_OUTPUT_FORMAT,
    FFMPEG_AUDIO_CODEC
)

WAV_SAMPLE_RATE = 16000  # 16kHz 采样率
WAV_CHANNELS = 1         # 单声道
WAV_CODEC = "pcm_s16le"  # 16位PCM编码（WAV标准）


# 配置日志（复用项目日志规范）
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


async def save_upload_audio(file) -> tuple[bool, str]:
    """
    保存前端上传的音频文件到static/audio/uploads
    :param file: FastAPI的UploadFile对象
    :return: (是否成功, 文件路径/错误信息)
    """
    try:
        # 生成唯一文件名，避免覆盖
        file_ext = file.filename.split(".")[-1] if "." in file.filename else "webm"
        file_name = f"audio_{uuid.uuid4()}.{file_ext}"
        file_path = AUDIO_UPLOAD_DIR / file_name

        # 确保文件指针在开头
        await file.seek(0)
        
        # 使用异步方式读取文件内容
        content = await file.read()
        
        # 检查文件内容是否为空
        if not content or len(content) == 0:
            logging.error(f"上传的音频文件为空: {file.filename}")
            return False, "音频文件为空"
        
        logging.info(f"接收到音频文件: {file.filename}, 大小: {len(content)} bytes")

        # 同步写入文件（文件IO通常是阻塞的）
        with open(file_path, "wb") as f:
            f.write(content)

        logging.info(f"音频文件保存成功: {file_path}")
        return True, str(file_path)
    except Exception as e:
        logging.error(f"保存上传音频失败：{str(e)}")
        return False, str(e)




async def convert_webm_to_wav(input_path: str | Path) -> tuple[bool, str]:
    """
    将 WebM 文件转换为标准 WAV 格式（适配语音识别）
    如果输入已经是 WAV 文件，则直接返回
    :param input_path: 音频文件路径
    :return: (转换是否成功, 输出WAV路径/错误信息)
    """
    input_path = Path(input_path)
    if not input_path.exists():
        return False, f"文件不存在：{input_path}"
    
    # 检查输入文件大小
    file_size = input_path.stat().st_size
    logging.info(f"输入文件大小: {file_size} bytes")
    
    if file_size == 0:
        return False, "输入文件为空"

    # 如果已经是 WAV 文件，直接返回
    if input_path.suffix.lower() == ".wav":
        logging.info(f"文件已经是 WAV 格式，无需转换：{input_path}")
        return True, str(input_path)

    # 生成 WAV 输出文件名
    output_file_name = f"audio_{uuid.uuid4()}.wav"
    output_path = AUDIO_OUTPUT_DIR / output_file_name

    def _convert():
        try:
            logging.info(f"开始转换音频: {input_path} -> {output_path}")
            
            # 首先获取输入音频的信息
            # 修改后（强行指定 D 盘路径）：
            ffprobe_path = r"D:\ffmpeg\bin\ffprobe.exe" if os.path.exists(r"D:\ffmpeg\bin\ffprobe.exe") else "ffprobe"
            probe = ffmpeg.probe(str(input_path), cmd=ffprobe_path)
            audio_info = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
            input_sample_rate = int(audio_info.get('sample_rate', 48000))
            input_channels = int(audio_info.get('channels', 2))
            
            logging.info(f"输入音频信息: 采样率={input_sample_rate}Hz, 声道数={input_channels}")
            
            # 阿里云ASR推荐16kHz
            output_sample_rate = 16000
            
            logging.info(f"转换参数: 输出采样率={output_sample_rate}Hz, 声道数=1")
            
            # 构建音频过滤器链 - 只在af中处理重采样，不在ar参数中重复指定
            # 如果输入是立体声，先转为单声道，然后重采样到16kHz
            if input_channels > 1:
                audio_filter = f'pan=mono|c0=0.5*c0+0.5*c1,volume=2.0,aresample={output_sample_rate}'
            else:
                audio_filter = f'aresample={output_sample_rate}'
            
            # 使用ffmpeg-python构建命令
            stream = ffmpeg.input(str(input_path))
            stream = ffmpeg.output(
                stream,
                str(output_path),
                format="wav",
                acodec="pcm_s16le",
                ac=1,  # 单声道
                vn=True,  # 去掉视频轨
                y=None,   # 覆盖已有文件
                af=audio_filter  # 音频过滤器（包含重采样）
            )
            
            ffmpeg_path = r"D:\ffmpeg\bin\ffmpeg.exe" if os.path.exists(r"D:\ffmpeg\bin\ffmpeg.exe") else "ffmpeg"
            ffmpeg.run(stream, quiet=True, capture_stderr=True, cmd=ffmpeg_path)
            
            # 检查输出文件
            if output_path.exists():
                output_size = output_path.stat().st_size
                logging.info(f"WebM转WAV成功：{input_path} -> {output_path}, 输出大小: {output_size} bytes")
                
                # 验证输出文件是否为有效的WAV格式（检查文件头）
                with open(output_path, 'rb') as f:
                    header = f.read(12)  # 读取RIFF头
                    if header[:4] == b'RIFF' and header[8:12] == b'WAVE':
                        logging.info(f"验证通过：输出文件是有效的WAV格式")
                    else:
                        logging.warning(f"验证警告：输出文件可能不是标准WAV格式，文件头: {header[:12].hex()}")
                
                return True, str(output_path)
            else:
                return False, "转换后的文件不存在"
                
        except ffmpeg.Error as e:
            err_msg = f"FFmpeg转码失败：{e.stderr.decode('utf-8') if e.stderr else str(e)}"
            logging.error(err_msg)
            return False, err_msg
        except Exception as e:
            err_msg = f"转换异常：{str(e)}"
            logging.error(err_msg)
            return False, err_msg

    # 在后台线程中执行转换，避免阻塞事件循环
    return await asyncio.to_thread(_convert)

def get_backup_wav() -> str:
    """获取兜底WAV文件（转换失败时返回）"""
    backup_files = list(AUDIO_BACKUP_DIR.glob("*.wav"))
    if backup_files:
        return str(backup_files[0])
    return ""