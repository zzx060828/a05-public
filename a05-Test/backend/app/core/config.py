import os
from pathlib import Path

# 原有配置（保留不动）
# 示例：数据库配置、项目端口等
DATABASE_URL = "sqlite:///./interview_business.db"
API_V1_STR = "/api"
PORT = 8001

# 新增：音频相关配置（贴合现有static/audio/uploads目录）
BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = BASE_DIR / "static"
AUDIO_ROOT = STATIC_DIR / "audio"# backend根目录
AUDIO_UPLOAD_DIR = BASE_DIR / "static" / "audio" / "uploads"  # 复用原有uploads目录
AUDIO_OUTPUT_DIR = BASE_DIR / "static" / "audio" / "output"
AUDIO_BACKUP_DIR = BASE_DIR / "static" / "audio" / "backup"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 最大上传文件：10MB

# 自动创建output/backup目录（uploads已存在）
for dir_path in [AUDIO_OUTPUT_DIR, AUDIO_BACKUP_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# FFmpeg转换配置
FFMPEG_OUTPUT_FORMAT = "wav"
FFMPEG_AUDIO_CODEC = "pcm_s16le"