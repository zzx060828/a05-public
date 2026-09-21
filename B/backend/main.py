# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.datebase import engine,Base
from app.api.v1 import auth, jobs, candidates, questions

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI 面试企业端后端 API",
    version="1.0.0",
    description="支持岗位发布、多租户鉴权、C端面试数据回调以及候选人AI报告深度解析"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由
app.include_router(auth.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(candidates.router, prefix="/api/v1") # 👈 新增候选人看板与报告接口
app.include_router(questions.router, prefix="/api/v1") # 👈 题库代理：转发至 C端

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8002, reload=True)