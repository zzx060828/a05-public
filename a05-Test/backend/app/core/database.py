from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import datetime
from sqlalchemy import JSON  # 确保头部引入了 JSON

# 共享 B端数据库，实现 BC 联调（表结构已对齐）
from pathlib import Path as _Path
_DB_PATH = _Path(__file__).resolve().parent.parent.parent.parent.parent / "B" / "backend" / "interview_business.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{_DB_PATH.as_posix()}"
SQLALCHEMY_ASYNC_DATABASE_URL = f"sqlite+aiosqlite:///{_DB_PATH.as_posix()}"

# 同步数据库引擎和会话
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
B_SessionLocal = SessionLocal  # 共享 DB 后就是同一个

# 异步数据库引擎和会话
async_engine = create_async_engine(
    SQLALCHEMY_ASYNC_DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    password_hash = Column(String(256), nullable=False)

class InterviewRecord(Base):
    __tablename__ = "interview_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)      # 会话唯一标识
    user_id = Column(Integer, index=True)        # 用户ID，用于查询用户所有对话
    user_text = Column(Text)                    # 用户回答文本
    ai_reply = Column(Text)                     # AI 回复内容
    scores = Column(JSON)                       # 存储五维评分字典
    analysis = Column(Text)                     # 存储分析结果（字符串格式）
    report_content = Column(Text, nullable=True)# 存储markdown报告
    timestamp = Column(DateTime, default=datetime.datetime.utcnow,index=True)

class InterviewReport(Base):
    __tablename__ = "interview_reports"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)      # 会话唯一标识
    user_id = Column(Integer, index=True)        # 用户ID，用于查询用户所有报告
    job_id = Column(Integer, index=True, nullable=True)
    score=Column(Integer, nullable=True)
    report_content = Column(Text, nullable=False)  # 报告内容（Markdown格式）
    generated_at = Column(DateTime, default=datetime.datetime.utcnow)  # 生成时间
class JobPosition(Base):
    __tablename__ = "job_positions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    enterprise_id = Column(Integer, nullable=False, comment="企业ID")
    token = Column(String, unique=True, index=True, nullable=False)
    title = Column(String(100), nullable=False, comment="岗位名称(如:Java开发)")
    department = Column(String(100), nullable=True)
    difficulty = Column(String(20), default="Medium", comment="难度")
    status = Column(String(20), default="open", comment="状态: open/closed")
    max_participants = Column(Integer, default=50)  # 面试人数上限
    cmci_value = Column(Float, default=0.75)  # CMCI 配置值


class QuestionBank(Base):
    """导览/知识库 题库表（完全对齐原始 JSON 属性）"""
    __tablename__ = "question_bank"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False, index=True)  # 用于存放 python_knowledge, common_behavior 等复合标签

    # 纯原生字段
    core_entity = Column(String, nullable=True)  # 核心实体
    question = Column(Text, nullable=False)  # 问题
    answer = Column(Text, nullable=True)  # 回答
    difficulty = Column(String, nullable=True, index=True)  # 难度

    # 支持原生存储打分点和标准的 JSON 字段
    expected_answer_points = Column(JSON, nullable=True)  # 期望回答点
    scoring_points = Column(JSON, nullable=True)  # 得分标准

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# 自动创建表结构
Base.metadata.create_all(bind=engine)

# 异步版本的表结构创建（可选，用于初始化）
async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)