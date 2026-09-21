# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, DeclarativeBase
from ..core.config import require_env

# 1. 配置你的数据库连接 URL (请替换为你自己的 MySQL / PostgreSQL 用户名、密码、端口、库名)
# 格式: 数据库类型+驱动://用户名:密码@主机地址:端口/数据库名
SQLALCHEMY_DATABASE_URL = require_env("DATABASE_URL")

# 2. 创建 SQLAlchemy 数据库引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,          # 开启后会在控制台打印执行的 SQL 语句，方便调试
    pool_pre_ping=True  # 防止数据库连接断开
)

# 3. 创建本地会话工厂（用于依赖注入中获取数据库操作对象 DB Session）
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. 【核心定义】创建 Base 基类
# 现代 SQLAlchemy 2.0 推荐使用继承 DeclarativeBase 的写法：
class Base(DeclarativeBase):
    pass

# （如果你用的 SQLAlchemy 较老，也可以用下面这行代替上面的 class 定义：）
# Base = declarative_base()


# 5. 提供给 FastAPI 路由使用的获取数据库会话的依赖函数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
