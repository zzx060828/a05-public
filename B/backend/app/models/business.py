# app/models/business.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, ForeignKey
from datetime import datetime
from ..core.datebase import Base

class JobPosition(Base):
    __tablename__ = "job_positions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    enterprise_id = Column(Integer, nullable=False, comment="企业ID")
    title = Column(String(100), nullable=False, comment="岗位名称(如:Java开发)")
    department = Column(String(100), nullable=True)
    difficulty = Column(String(20), default="Medium", comment="难度")
    status = Column(String(20), default="open", comment="状态: open/closed")
    token = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    max_participants = Column(Integer, default=50)  # 面试人数上限
    cmci_value = Column(Float, default=0.75)  # CMCI 配置值
    rag_id = Column(String(50), nullable=True, comment="关联RAG题库ID")

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

class InterviewReport(Base):
    __tablename__ = "interview_reports"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)      # 会话唯一标识
    user_id = Column(Integer, index=True)        # 用户ID，用于查询用户所有报告
    job_id = Column(Integer, index=True, nullable=True)
    score = Column(Integer, nullable=True)
    report_content = Column(Text, nullable=False)  # 报告内容（Markdown格式）
    generated_at = Column(DateTime, default=datetime.utcnow)  # 生成时间



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
