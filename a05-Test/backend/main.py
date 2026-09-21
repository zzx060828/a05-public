# backend/main.py
import shutil
import subprocess
import sys
import logging
import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

# 原有依赖 (严格保持你最初的样子，绝不乱加)
from app.core.database import Base, engine
from app.core.data_initializer import auto_import_json
from app.core.cache import RedisCache

# 日志配置
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s", 
    datefmt="%Y-%m-%d %H:%M:%S"
)

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("项目根目录：", project_root)

from app.api.endpoints import router as api_router

app = FastAPI(title="Business Backend")
cache = RedisCache()
Base.metadata.create_all(bind=engine)

@app.on_event("startup")
async def startup_event():
    auto_import_json()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_static = os.path.join(project_root, "ai_module", "static")
if os.path.exists(ai_static):
    app.mount("/static", StaticFiles(directory=ai_static), name="static")

def check_and_install_ffmpeg():
    if shutil.which("ffmpeg"): return
    try: 
        subprocess.run(["winget", "install", "ffmpeg", "--accept-source-agreements", "--accept-package-agreements"], capture_output=True, text=True, shell=True)
    except Exception: pass

app.include_router(api_router, prefix="/api")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"全局异常: {str(exc)}", exc_info=True)
    return JSONResponse(status_code=500, content={"status": "error", "message": "服务器内部错误"})

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    import time
    start_time = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(time.time() - start_time)
    return response


@app.get("/")
def read_root():
    return {"message": "Backend 8001 is running"}

if __name__ == "__main__":
    if os.name == 'nt':
        check_and_install_ffmpeg()
    
    # 彻底关掉 reload，防止 ChromaDB 锁文件导致的无限重启地雷
    uvicorn.run("main:app", host="0.0.0.1", port=8001)