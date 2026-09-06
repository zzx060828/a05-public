import base64
import hashlib
import hmac
import json
import logging
import os
import random
import secrets
import shutil
import sys
import time
import uuid
import re
import asyncio
import functools
import contextlib
from datetime import datetime, timedelta
from pathlib import Path as FilePath  # 1. 使用 FilePath 避免与 FastAPI 的 Path 冲突
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..core.database import QuestionBank, JobPosition
from sqlalchemy import or_
from ..services.deduplication_service import deduplicator_instance
# JWT相关导入
import jwt
from fastapi import BackgroundTasks


import aiohttp
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# 全局HTTP连接池
session = None

# 获取HTTP会话
async def get_http_session():
    global session
    if session is None or session.closed:
        session = aiohttp.ClientSession()
    return session

# 性能监控装饰器
def performance_monitor(func):
    """性能监控装饰器"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        logging.info(f"开始执行: {func.__name__}")
        
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logging.info(f"执行完成: {func.__name__}, 耗时: {execution_time:.4f}秒")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logging.error(f"执行失败: {func.__name__}, 耗时: {execution_time:.4f}秒, 错误: {str(e)}", exc_info=True)
            raise
    return wrapper

# 临时文件管理上下文管理器
@contextlib.asynccontextmanager
async def temp_file_manager():
    """临时文件管理上下文管理器"""
    temp_files = []
    try:
        yield temp_files
    finally:
        # 只注释掉下面这段逻辑，保留函数骨架
        for f in temp_files:
            if f and os.path.exists(f):
                try:
                    # os.remove(f)  <-- 核心：把这一行注释掉即可
                    logging.info(f"已跳过清理，保留文件以供检查: {f}")
                except Exception as e:
                    logging.error(f"清理临时文件失败: {str(e)}")

# FastAPI 相关导入
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Path, BackgroundTasks, Request, Security
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse,JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

# 2. 核心路径逻辑：统一使用 FilePath (pathlib) 处理
# __file__ 是 .../backend/app/api/endpoints.py
# .resolve().parents[3] 直接跳 4 级到达 a05-main 根目录
PROJECT_ROOT = FilePath(__file__).resolve().parents[3]

# 3. 将根目录加入 sys.path 以确保能找到 ai_module
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 4. 业务模块导入 (务必在 sys.path 修改后进行)
try:
    from ai_module.stt_aliyun import speech_to_text
    logging.info("ai_module 导入成功")
except ImportError as e:
    logging.error(f"ai_module 导入失败，当前计算的项目根路径为: {PROJECT_ROOT}")
    logging.error(f"具体错误: {e}")
    speech_to_text = None

# 5. 内部模块导入
from ..core.config import API_V1_STR, MAX_FILE_SIZE, AUDIO_UPLOAD_DIR, AUDIO_OUTPUT_DIR
from ..core.database import User, SessionLocal, InterviewSession, InterviewRecord, InterviewReport
from ..services.audio_service import save_upload_audio, convert_webm_to_wav, get_backup_wav
from ..services.interview_service import InterviewService

router = APIRouter()
security=HTTPBearer()

# --- 后续定义 Pydantic 模型和 API 路由 ---
# --- 数据库依赖 ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 异步数据库依赖 ---
async def get_async_db():
    from ..core.database import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# --- JWT认证依赖 ---
def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """获取当前用户"""
    # 从Authorization头中获取token
    token = credentials.credentials
    
    # 如果Authorization头中没有token，尝试从查询参数中获取
    if not token:
        raise HTTPException(status_code=401, detail="未提供认证令牌")
    
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="无效的认证令牌")
    
    return payload


# --- 请求模型 (Schemas) ---
class StartRequest(BaseModel):
    session_id: str = Field(..., description="会话唯一ID")
    token: Optional[str] = Field(None, description="安全邀请Token")
    target_role: str = Field(default="Java后端开发工程师", description="面试岗位")
    experience: str = Field(default="middle", description="经验等级")
    type: str = Field(default="coach", description="面试类型")
    difficulty: int = Field(default=3, description="面试难度")
    resumeText: str = Field(default="", description="简历文本内容")

    jobRequirements: str = Field(default="", description="目标岗位要求")

class ChatRequest(BaseModel):
    session_id: str = Field(..., description="会话唯一ID")
    user_text: str = Field(..., description="用户回答文本")
    speech_meta: dict = Field(default={"speed": "正常", "pause_count": 0}, description="语音特征")


class ReportRequest(BaseModel):
    session_id: str = Field(..., description="会话唯一ID")
    token: Optional[str] = Field(None, description="从URL中获取的安全Token")

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=12, description="用户名，仅支持英文和数字，2-12位")
    password: str = Field(..., min_length=6, max_length=12, description="密码,仅支持英文和数字，6-12位")

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=12, description="用户名，仅支持英文和数字，6-12位")
    password: str = Field(..., min_length=6, max_length=12, description="密码，仅支持英文和数字，6-12位")

# 🌟 新增：支持中文的用户名校验
def validate_username(text: str) -> None:
    """校验用户名：支持中文、英文、数字，不允许包含特殊符号"""
    # \u4e00-\u9fa5 是汉字的 Unicode 范围
    pattern = re.compile(r'^[\u4e00-\u9fa5A-Za-z0-9]+$')
    if not pattern.match(text):
        raise HTTPException(
            status_code=400,
            detail="用户名仅支持中文、英文和数字，不允许包含特殊符号"
        )

# 🌟 保留原样：密码依然只能是英文和数字，防乱码
def validate_password(text: str) -> None:
    """校验密码：仅支持英文和数字"""
    pattern = re.compile(r'^[A-Za-z0-9]+$')
    if not pattern.match(text):
        raise HTTPException(
            status_code=400,
            detail="密码仅支持英文和数字，不允许包含特殊符号"
        )

# JWT配置
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 52560000

_TOKENS: dict[str, int] = {}

def _hash_password(password: str) -> str:
    iterations = 120_000
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, dklen=32)
    return "pbkdf2_sha256$%d$%s$%s" % (
        iterations,
        base64.b64encode(salt).decode("ascii"),
        base64.b64encode(dk).decode("ascii"),
    )

def _verify_password(password: str, stored: str) -> bool:
    try:
        scheme, iters_s, salt_b64, dk_b64 = stored.split("$", 3)
        if scheme != "pbkdf2_sha256":
            return False
        iterations = int(iters_s)
        salt = base64.b64decode(salt_b64.encode("ascii"))
        expected = base64.b64decode(dk_b64.encode("ascii"))
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, dklen=len(expected))
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建JWT访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """验证JWT令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

# --- API 接口实现 ---

@router.post("/auth/register")
async def register(req: RegisterRequest, db: Session = Depends(get_db)):
    username = req.username.strip()
    password = req.password.strip()
    validate_username(username)
    validate_password(password)

    if not username:
        raise HTTPException(status_code=400, detail="用户名不能为空")
    if not password:
        raise HTTPException(status_code=400, detail="密码不能为空")

    from ..core.database import User
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="账号已存在")

    # 步骤5：密码加密 + 写入数据库（原有逻辑）
    try:
        password_hash = _hash_password(password)
        new_user = User(username=username, password_hash=password_hash)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logging.info(f"用户注册成功：{username}")
        return JSONResponse(
            status_code=200,
            content={"status": "success", "msg": "注册成功", "user_id": new_user.id}
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="账号已存在（并发冲突）")
    except Exception as e:
        db.rollback()
        logging.error(f"注册失败：{str(e)}")
        raise HTTPException(status_code=500, detail=f"服务器错误：{str(e)}")

@router.post("/auth/login")
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    username = req.username.strip()
    user = db.query(User).filter(User.username == username).first()
    if not user or not _verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="账号或密码错误")

    # 使用JWT生成token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=access_token_expires
    )
    
    return {"status": "success", "token": access_token, "user_id": user.id, "username": user.username}

# 在 endpoints.py 中修改 start_interview 函数
@router.post("/start")
@performance_monitor
async def start_interview(
        req: StartRequest,  # 确保你的 StartRequest 模型里包含 token 字段
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    print("================== 成功进入 /start 接口 ==================")

    target_role = "后端开发工程师"  # 默认兜底
    difficulty = "Medium"
    job_id = None

    if req.target_role.strip():
        target_role = req.target_role.strip()
    difficulty = str(req.difficulty)

    # 🌟 核心：通过前端传过来的 token 去数据库反查岗位信息
    token = getattr(req, "token", None)
    if token:
        job_record = db.query(JobPosition).filter(
            JobPosition.token == token,
            JobPosition.status == "open"
        ).first()

        if job_record:
            job_id = job_record.id
            target_role = job_record.title  # 成功拿到真正的岗位名称（比如：前端开发工程师）
            difficulty = job_record.difficulty  # 拿到该岗位对应的难度
            print(f"🎯 成功通过 token 锁定岗位: token={token} -> 岗位={target_role}")
        else:
            print(f"⚠️ 警告：通过 token={token} 没有在数据库中找到对应的有效岗位！")

    # 准备传递给 AI 模块的参数
    ai_params = {
        "target_role": target_role,
        "difficulty": difficulty,
        "job_id": job_id,
        "mode": req.type if req.type in ["coach", "exam"] else "coach",
        "resume_text": getattr(req, "resumeText", ""),
        "job_description": getattr(req, "jobRequirements", "")
    }

    print(f"🚀 最终发送给 AI 的参数: {ai_params}")

    result = await InterviewService.call_ai_start(ai_params)
    if result.get("status") != "success":
        return result

    session_id = result.get("session_id") or result.get("sessionId")
    if not session_id:
        raise HTTPException(status_code=502, detail="AI service did not return a session ID")

    user_id = int(current_user.get("sub"))
    persisted_session = InterviewSession(
        session_id=session_id,
        user_id=user_id,
        job_id=job_id,
        target_role=target_role,
        difficulty=difficulty,
        mode=ai_params["mode"],
        resume_text=ai_params["resume_text"],
        job_description=ai_params["job_description"],
        first_question=result.get("reply_text"),
        status="active",
    )
    try:
        db.add(persisted_session)
        db.commit()
    except Exception:
        db.rollback()
        raise

    result["persisted"] = True
    return result
@router.post("/chat")
@performance_monitor
async def chat_with_text(req: ChatRequest, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """纯文字对话：调用 AI 并持久化存储"""
    user_id = int(current_user.get("sub"))
    stored_session = db.query(InterviewSession).filter(
        InterviewSession.session_id == req.session_id
    ).first()
    if stored_session and stored_session.user_id != user_id:
        raise HTTPException(status_code=403, detail="Session does not belong to the current user")

    logging.info(f"开始文字对话: session_id={req.session_id}, user_id={current_user.get('sub')}")
    result = await InterviewService.call_ai_chat(req.model_dump())

    if result.get("status") == "success":
        data = result.get("data", {})
        # 存储到 8001 的本地数据库
        if stored_session is None:
            stored_session = InterviewSession(
                session_id=req.session_id,
                user_id=user_id,
                target_role="unknown",
                mode="coach",
                status="active",
            )
            db.add(stored_session)

        new_record = InterviewRecord(
            session_id=req.session_id,
            user_id=user_id,
            user_text=req.user_text,
            ai_reply=data.get("reply_to_user"),
            scores=data.get("scores"),
            analysis=json.dumps(data.get("analysis", {}))
        )
        db.add(new_record)
        stored_session.turn_count = (stored_session.turn_count or 0) + 1
        stored_session.updated_at = datetime.utcnow()
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        logging.info("对话记录保存成功")

        # ==========================================
        # 🔴 关键修改：把数据展平返回给前端，透传音频链接
        # ==========================================
        return {
            "status": "success",
            "user_text": req.user_text,
            "reply": data.get("reply_to_user"),
            "reply_text": data.get("reply_to_user"),
            "reply_audio_url": data.get("reply_audio_url"), # ✨ 这里接住 8000 传来的音频链接！
            "scores": data.get("scores", {}),
            "analysis": data.get("analysis", {}),
            "thought_process": data.get("thought_process", ""),
            "think_aloud": data.get("think_aloud", {}),
            "suggestion": data.get("suggestion", ""),
            "next_action": data.get("next_action", "追问")
        }
        
    return result


@router.post("/chat_with_audio")
@performance_monitor
async def chat_with_audio(
        session_id: str = Form(...),  # 匹配前端 fd.append('session_id')
        audio_file: UploadFile = File(...),
        image_file: Optional[UploadFile] = File(None),  # 匹配前端 fd.append('image_file')
        db: AsyncSession = Depends(get_async_db),
        current_user: dict = Depends(get_current_user)
):
    user_id = int(current_user.get("sub"))
    session_query = await db.execute(
        select(InterviewSession).where(InterviewSession.session_id == session_id)
    )
    stored_session = session_query.scalar_one_or_none()
    if stored_session and stored_session.user_id != user_id:
        raise HTTPException(status_code=403, detail="Session does not belong to the current user")

    async with temp_file_manager() as temp_files:
        try:
            logging.info(f"开始处理音频文件: {audio_file.filename}, session_id: {session_id}, user_id: {current_user.get('sub')}")
            save_dir = FilePath(PROJECT_ROOT) / "static" / "audio" / "uploads"
            os.makedirs(save_dir, exist_ok=True)
            # 1. 保存原始音频文件
            save_ok, save_result = await save_upload_audio(audio_file)
            if not save_ok:
                raise Exception(f"文件保存失败: {save_result}")
            temp_files.append(save_result)
            logging.info(f"音频文件保存成功: {save_result}")

            # 2. 异步转码为 WAV (供 STT 识别)
            convert_ok, wav_path = await convert_webm_to_wav(save_result)
            if not convert_ok:
                raise Exception("音频转码失败")

            temp_files.append(wav_path)
            logging.info(f"音频转码成功: {wav_path}")
            logging.info(f"DEBUG 发送给AI模块的文件路径: {wav_path}") #

            # 3. 转发给 AI 模块并获取结果
            # 使用转码后的 WAV 文件，而不是原始文件
            logging.info("开始调用 AI 模块")
            ai_resp = await InterviewService.call_ai_chat_with_audio(
                session_id=session_id,
                audio_file_path=wav_path,  # 传递 WAV 文件路径
                image_file=image_file
            )

            if ai_resp.get("status") != "success":
                error_msg = ai_resp.get("message", "")
                # 🔴 拦截“听不清”的错误，进行优雅降级
                if "识别结果为空" in error_msg or "识别失败" in error_msg:
                    logging.warning("语音未识别到内容，触发温柔提示")
                    fallback_msg = "抱歉，我刚刚没有听清。可能是因为环境有点嘈杂或者声音太小了，能麻烦您靠近麦克风大声再说一遍吗？"
                    return {
                        "status": "success",
                        "user_text": "[未听清您的发言]",
                        "reply": fallback_msg,
                        "reply_text": fallback_msg,  # 🔴 关键！加上这个，前端 UI 就能更新了
                        "reply_audio_url": "",       # 🔴 补上空音频链接，防止前端播放器报错
                        "scores": {},
                        "analysis": {},
                        "thought_process": "未检测到有效语音输入，引导用户重试。",
                        "suggestion": "建议在相对安静的环境下面试，并适当提高说话音量哦。",
                        "multimodal_features": {
                            "emotion_trajectory": "暂无",
                            "emotion_probs": {},
                            "is_cmci_triggered": False
                        }
                    }
                else:
                    # 如果是其他严重错误（比如欠费了），还是继续报错
                    raise Exception(error_msg or "AI 模块调用失败")

            # AI模块直接返回数据，没有包装在data字段中
            # 但为了兼容性，我们检查是否有data字段
            ai_data = ai_resp.get("data") if ai_resp.get("data") else ai_resp
            logging.info(f"AI 模块返回数据: {ai_data}")

            # 使用AI模块返回的识别结果
            user_text = ai_data.get("user_text", "[未识别到有效语音]")
            # 注意：AI模块返回的字段名是 reply_text 和 reply_audio_url
            ai_reply = ai_data.get("reply_text", "") or ai_data.get("reply_to_user", "")
            reply_audio = ai_data.get("reply_audio_url") or ai_data.get("reply_audio")
            scores = ai_data.get("scores", {})
            analysis = ai_data.get("analysis", {})
            thought_process = ai_data.get("thought_process", "")
            think_aloud = ai_data.get("think_aloud", {})
            suggestion = ai_data.get("suggestion", "")

            # 4. 异步数据库记录
            if stored_session is None:
                stored_session = InterviewSession(
                    session_id=session_id,
                    user_id=user_id,
                    target_role="unknown",
                    mode="coach",
                    status="active",
                )
                db.add(stored_session)

            new_record = InterviewRecord(
                session_id=session_id,
                user_id=user_id,
                user_text=user_text,
                ai_reply=ai_reply,
                scores=scores,
                analysis=json.dumps(analysis)
            )
            db.add(new_record)
            stored_session.turn_count = (stored_session.turn_count or 0) + 1
            stored_session.updated_at = datetime.utcnow()
            try:
                await db.commit()
            except Exception:
                await db.rollback()
                raise
            await db.refresh(new_record)
            logging.info(f"数据库记录成功: {new_record.id}")

            # 5. 返回 JSON 给前端 (匹配 axios 的 response.data)
            # 返回AI模块的所有字段
            return {
                "status": "success",
                "user_text": user_text,
                "reply": ai_reply,
                "scores": scores,
                "analysis": analysis,
                "thought_process": thought_process,
                "think_aloud": think_aloud,
                "suggestion": suggestion,
                "reply_text": ai_reply,
                "reply_audio_url": reply_audio,
                "multimodal_features": ai_data.get("multimodal_features", {
                    "emotion_trajectory": "暂无",
                    "emotion_probs": {},
                    "is_cmci_triggered": False
                })
            }

        except Exception as e:
            logging.error(f"接口报错: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": str(e)}
            )


@router.post("/upload_frame", summary="接收前端每5秒传来的实时截图")
async def upload_frame(
    session_id: str = Form(...),
    screenshot: UploadFile = File(...),
    current_user: dict = Depends(get_current_user) # 🔴 加上 JWT 鉴权，保护接口
):
    try:
        # 1. 确保保存图片的文件夹存在
        import os
        save_dir = FilePath(PROJECT_ROOT) / "static" / "images"
        os.makedirs(save_dir, exist_ok=True)
        
        # 2. 把前端发来的图片保存到本地
        file_path = save_dir / f"{session_id}_{screenshot.filename}"
        with open(file_path, "wb") as f:
            f.write(await screenshot.read())
            
        logging.info(f"📸 成功接收实时截图，保存路径: {file_path}")
        
        # TODO: 未来如果你需要让 8000 端口的大模型分析这张图，
        # 可以在这里把 file_path 放进 Redis 或者通过内部请求推给 8000。
        
        return {"status": "success", "msg": "实时帧接收成功"}
        
    except Exception as e:
        logging.error(f"❌ 实时截图接收失败: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"服务器内部错误: {str(e)}"}
        )

@router.post(f"{API_V1_STR}/audio/convert", tags=["音频转换"], summary="WebM转WAV（AI面试专用）")
async def audio_convert(
        file: UploadFile = File(..., description="上传WebM格式录音文件"),
        background_tasks: BackgroundTasks = BackgroundTasks()
):
    if file.content_type != "video/webm":
        raise HTTPException(status_code=400, detail="仅支持WebM格式")
    # 1. 校验文件大小
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件超过最大限制（{MAX_FILE_SIZE // 1024 // 1024}MB）"
        )

    # 2. 保存上传文件到static/audio/uploads
    save_ok, save_result = await save_upload_audio(file)
    if not save_ok:
        raise HTTPException(status_code=500, detail=f"文件保存失败：{save_result}")

    # 3. 转换WebM到WAV
    convert_ok, convert_result = convert_webm_to_wav(save_result)
    if convert_ok:
        # 返回转换后的M4A文件
        return FileResponse(
            path=convert_result,
            filename=os.path.basename(convert_result),
            media_type="audio/wav"  # M4A标准MIME类型
        )
    else:
        # 转换失败：返回兜底文件
        backup_file = get_backup_wav()
        if not backup_file:
            raise HTTPException(
                status_code=500,
                detail=f"转换失败且无兜底文件：{convert_result}"
            )
        return FileResponse(
            path=backup_file,
            filename="backup_interview.wav",
            media_type="audio/wav"
        )


# 可选：清理过期音频文件接口（演示/运维用）
@router.delete(f"{API_V1_STR}/audio/clean", tags=["音频转换"], summary="清理过期音频文件")
async def clean_audio_files():
    import time
    from ..core.config import AUDIO_UPLOAD_DIR, AUDIO_OUTPUT_DIR

    def _clean_expired(dir_path: Path, hours: int = 1):
        now = time.time()
        for file in dir_path.glob("*"):
            if file.is_file() and os.path.getmtime(file) < now - hours * 3600:
                os.remove(file)
                logging.info(f"清理过期文件：{file}")

    _clean_expired(AUDIO_UPLOAD_DIR)
    _clean_expired(AUDIO_OUTPUT_DIR)
    return {"code": 200, "msg": "过期音频清理完成"}


# 注意：在参数里加上了 background_tasks: BackgroundTasks
@router.post("/report")
async def get_report(
        req: ReportRequest,  # 假设 ReportRequest 里面包含 session_id 和 token
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    user_id = int(current_user.get('sub'))

    stored_session = db.query(InterviewSession).filter(
        InterviewSession.session_id == req.session_id
    ).first()
    if stored_session and stored_session.user_id != user_id:
        raise HTTPException(status_code=403, detail="Session does not belong to the current user")

    try:
        # 1. 核心：通过前端传过来的 token，去 JobPosition 表里反查出对应的 job_id

        real_job_id = None
        token = getattr(req, "token", None)

        # 1. 🌟 修改点：改成“选填”逻辑。有 token 才去反查岗位，没有就不查
        if token:
            job_record = db.query(JobPosition).filter(
                JobPosition.token == token,
                JobPosition.status == "open"
            ).first()

            if job_record:
                real_job_id = job_record.id


        # 2. 调用 AI 服务生成全量报告 JSON
        result = await InterviewService.get_final_report_json({"session_id": req.session_id})

        if result.get("status") == "success":
            result["job_id"] = real_job_id
            score = result.get("match_score")
            report_str = json.dumps(result, ensure_ascii=False)

            new_report = db.query(InterviewReport).filter(
                InterviewReport.session_id == req.session_id,
                InterviewReport.user_id == user_id,
            ).first()
            if new_report is None:
                new_report = InterviewReport(
                    session_id=req.session_id,
                    user_id=user_id,
                )
                db.add(new_report)

            new_report.job_id = real_job_id
            new_report.score = float(score) if score is not None else None
            new_report.report_content = report_str

            if stored_session is None:
                stored_session = InterviewSession(
                    session_id=req.session_id,
                    user_id=user_id,
                    job_id=real_job_id,
                    target_role="unknown",
                    mode="coach",
                )
                db.add(stored_session)
            stored_session.job_id = real_job_id or stored_session.job_id
            stored_session.status = "completed"
            stored_session.completed_at = datetime.utcnow()
            stored_session.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(new_report)

            # 4. 把刚刚生成的 record_id 塞进返回结果中给前端
            if isinstance(result, dict):
                result["record_id"] = new_report.id

        return result
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history_conversations")
async def get_interview_conversations(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """获取当前用户的所有历史对话记录"""
    user_id = int(current_user.get('sub'))
    logging.info(f"获取用户所有对话记录: user_id={user_id}")
    # 只查询非报告类型的记录
    records = db.query(InterviewRecord).filter(
        InterviewRecord.user_id == user_id,
        InterviewRecord.user_text != "[SYSTEM_GENERATE_REPORT]"
    ).order_by(InterviewRecord.timestamp.desc()).all()
    history = []
    for r in records:
        try:
            analysis = json.loads(r.analysis) if r.analysis else {}
        except:
            analysis = r.analysis
        history.append({
            "id": r.id,
            "session_id": r.session_id,
            "user": r.user_text,
            "ai": r.ai_reply,
            "scores": r.scores,
            "analysis": analysis,
            "time": r.timestamp
        })
    return {
        "status": "success",
        "conversations": history,
        "total": len(history)
    }

@router.get("/history_reports")
async def get_interview_reports(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """获取当前用户的所有历史报告"""
    user_id = int(current_user.get('sub'))
    logging.info(f"获取用户所有历史报告: user_id={user_id}")
    reports = db.query(InterviewReport).filter(InterviewReport.user_id == user_id).order_by(InterviewReport.generated_at.desc()).all()
    report_list = []
    for report in reports:
        report_list.append({
            "id": report.id,
            "session_id": report.session_id,
            "job_id": report.job_id,
            "score": report.score,
            "content": report.report_content,
            "generated_at": report.generated_at
        })
    return {
        "status": "success",
        "reports": report_list,
        "total": len(report_list)
    }


@router.get("/history_sessions")
async def get_interview_sessions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Return the persisted lifecycle of the current user's interviews."""
    user_id = int(current_user.get("sub"))
    sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == user_id
    ).order_by(InterviewSession.started_at.desc()).all()
    return {
        "status": "success",
        "sessions": [
            {
                "session_id": item.session_id,
                "job_id": item.job_id,
                "target_role": item.target_role,
                "difficulty": item.difficulty,
                "mode": item.mode,
                "status": item.status,
                "turn_count": item.turn_count,
                "started_at": item.started_at,
                "updated_at": item.updated_at,
                "completed_at": item.completed_at,
            }
            for item in sessions
        ],
        "total": len(sessions),
    }

@router.get("/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取当前用户信息"""
    user_id = current_user.get('sub')
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {
        "status": "success",
        "user": {
            "id": user.id,
            "username": user.username
        }
    }


@router.get("/question_bank")
async def get_questions(
        category: Optional[str] = Query(None, description="分类标签，如 python_knowledge 或 common_behavior"),
        difficulty: str = Query("all", description="难度筛选: all, Easy, Medium, Hard"),
        keyword: Optional[str] = Query(None, description="搜索关键字"),  # 💡 1. 增加接收 keyword 参数
        page: int = Query(1, ge=1, description="当前页码"),
        limit: int = Query(10, ge=1, le=50, description="每页条数"),
        db: Session = Depends(get_db)
):
    """
    获取题库列表（支持按分类、难度、关键字筛选及真分页）
    """
    try:
        # 1. 基础分类查询
        query = db.query(QuestionBank)

        # 2. 如果前端传了 category 才加上过滤条件
        if category:
            query = query.filter(QuestionBank.category.contains(category))

        # 3. 动态过滤难度
        if difficulty and difficulty != "all":
            query = query.filter(QuestionBank.difficulty == difficulty)

        # 💡 4. 核心新增：模糊搜索逻辑！
        if keyword:
            # ilike 表示忽略大小写的模糊匹配，% 代表通配符
            query = query.filter(
                or_(
                    QuestionBank.core_entity.ilike(f"%{keyword}%"),
                    QuestionBank.question.ilike(f"%{keyword}%")
                )
            )

        # 5. 拿到该条件下全表的总条数
        total_count = query.count()

        # 6. 分页核心偏移量
        offset = (page - 1) * limit

        # 7. 执行真分页查询
        questions = query.offset(offset).limit(limit).all()

        # 8. 还原 JSON 原生结构吐给前端
        data_list = []
        for q in questions:
            data_list.append({
                "id": q.id,
                "core_entity": q.core_entity,
                "question": q.question,
                "answer": q.answer,
                "difficulty": q.difficulty,
                "expected_answer_points": q.expected_answer_points,
                "scoring_points": q.scoring_points
            })

        return {
            "status": "success",
            "data": data_list,
            "total": total_count,
            "page": page,
            "limit": limit
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"服务器内部错误: {str(e)}"
        }

import os
import json
import chromadb
from zhipuai import ZhipuAI
import logging
from sqlalchemy.orm import Session
from fastapi import Depends

# ==========================================
# 🌟 终极动态 RAG 接口：基于历史错题的千人千面推送
# ==========================================
# 你的 main.py 已经给 router 加了 prefix="/api"，所以这里直接写路径即可
@router.get("/rag/recommend_resources")
@router.get("/interview/recommend_resources") 
async def get_recommendation(
    session_id: str, 
    role: str, 
    db: Session = Depends(get_db) # 🌟 完美复用此文件的数据库会话
):
    try:
        # 动态计算 project_root (向上退到包含 ai_module 的目录)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 假设当前是 backend/app/api/endpoints.py，退4级就是项目根目录
        project_root = os.path.abspath(os.path.join(current_dir, "../../../.."))
        # 如果找不准，用绝对路径兜底计算
        if not os.path.exists(os.path.join(project_root, "ai_module")):
            project_root = os.path.abspath(os.path.join(os.getcwd(), ".."))
            
        db_path = os.path.join(project_root, "ai_module", "my_vector_db")
        
        logging.info(f"🚀 动态 RAG 接口被触发! session_id: {session_id}, role: {role}")

        # ==========================================
        # 🌟 核心：去 MySQL 里捞出这个 session_id 的所有聊天记录
        # ==========================================
        # 直接使用此文件顶部的 InterviewRecord 模型
        records = db.query(InterviewRecord).filter(
            InterviewRecord.session_id == session_id,
            InterviewRecord.user_text != "[SYSTEM_GENERATE_REPORT]"
        ).order_by(InterviewRecord.timestamp.asc()).all()

        weak_questions = []

        for r in records:
            # 解析单题的分析 JSON
            try:
                analysis = json.loads(r.analysis) if r.analysis else {}
            except:
                analysis = {} if not isinstance(r.analysis, dict) else r.analysis

            # 获取单题准确率
            scores_dict = analysis.get("scores", {}) if isinstance(analysis, dict) else {}
            acc = scores_dict.get("accuracy", 100)
            
            # 🌟 拦截低于 85 分的记录
            if isinstance(acc, (int, float)) and acc < 85:
                q_text = analysis.get("question", "")
                if not q_text:
                    q_text = r.user_text

                if q_text and str(q_text).strip():
                    weak_questions.append(str(q_text).strip())

        # ==========================================
        # 🌟 动态构建检索 Prompt
        # ==========================================
        if not weak_questions:
            search_query = f"[{role}] 核心架构与高级进阶面试指南"
            fallback_msg = "💡 您的基础非常扎实！以下为您推荐该岗位的高级进阶资料："
        else:
            weak_str = "、".join(weak_questions[:3]) 
            search_query = f"针对以下面试薄弱点的学习计划与突击资源：{weak_str}"
            fallback_msg = f"### 专属计划生成中\n\n💡 针对您的薄弱点（{weak_str}），题库正在加急收录相关进阶资料，请先参考基础面试大纲进行复习。"
            
        logging.info(f"🚀 动态 RAG 检索词: {search_query}")

        # ==========================================
        # 🌟 调用智谱并检索 ChromaDB
        # ==========================================
        zhipu_client = ZhipuAI(api_key=os.environ.get("ZHIPUAI_API_KEY", ""))
        response = zhipu_client.embeddings.create(model="embedding-2", input=search_query)
        query_vec = response.data[0].embedding
        
        chroma_client = chromadb.PersistentClient(path=db_path)
        collection = chroma_client.get_or_create_collection(name="learning_resources")
        
        results = collection.query(query_embeddings=[query_vec], n_results=1, where={"role": role})
        
        if results.get('metadatas') and len(results['metadatas']) > 0 and len(results['metadatas'][0]) > 0:
            content = results['metadatas'][0][0].get("markdown_content", "")
            if content:
                return {"status": "success", "resources": content}
        
        return {"status": "success", "resources": fallback_msg}
            
    except Exception as e:
        logging.error(f"❌ RAG 报错详情: {str(e)}")
        return {"status": "error", "message": f"AI 模块报错: {str(e)}"}
    

@router.post("/questions/import-check")
async def check_imported_questions(file: UploadFile = File(...)):
    # 1. 读出前端传上来的文件内容
    content = await file.read()
    new_questions = json.loads(content) 
    
    # 2. 从数据库获取已有题库 
    existing_questions = ["已有题目1", "已有题目2"] 
    
    # 🌟 修复 1：把 total 字段加上，这样前端就有数字了！
    report = {
        "total": len(new_questions), 
        "valid_items": [],
        "conflict_items": []
    }

    # 3. 调用你的 AI 服务进行查重
    for new_q in new_questions:
        # 🌟 修复 2：增加容错！如果找不到 question，就去里面找 topic
        query_text = new_q.get("question") or new_q.get("topic") or ""
        
        # 如果连 topic 都没有，说明格式真的不对，直接跳过或者记录为空
        if not query_text:
            continue
            
        # 调用 AI 查重
        is_dup, match_score, match_text = deduplicator_instance.is_semantically_duplicate(query_text, existing_questions)
        
        if is_dup:
            report["conflict_items"].append({
                "new_question": new_q,
                "conflict_with_db": match_text,
                "similarity_score": match_score
            })
        else:
            report["valid_items"].append(new_q)
            existing_questions.append(query_text) # 防止内部重复

    return {"status": "success", "data": report}
# ==========================================
# 🌟 演示专用：B/C端全静态 Mock 接口
# ==========================================

@router.post("/b_api/create_invitation")
async def mock_create_invitation():
    """B端创建面试链接（静态演示）"""
    # 永远返回一个固定的演示 Token
    demo_token = "DEMO-JAVA-888"
    demo_link = f"http://localhost:5173/formal?token={demo_token}"
    return {
        "status": "success", 
        "link": demo_link, 
        "token": demo_token,
        "msg": "面试邀请已生成"
    }

@router.get("/c_api/verify_token/{token}")
async def mock_verify_token(token: str):
    """C端校验 Token（静态演示）"""
    # 只要带有 Token，就给它返回一套极其专业的 JD 数据
    if token == "DEMO-JAVA-888":
        return {
            "status": "success", 
            "candidate_name": "张三 (演示候选人)",
            "job_title": "高级 Java 后端工程师",
            "requirements": "1. 精通 JVM 原理及调优；2. 熟悉高并发系统设计；3. 熟练掌握 Redis、Kafka 等中间件。"
        }
    else:
        return {"status": "error", "message": "无效的演示链接"}
