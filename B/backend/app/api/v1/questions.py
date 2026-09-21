# B端题库代理：转发至 C端/AI 后端 (8001)
import httpx
from fastapi import APIRouter, UploadFile, File, Depends
from app.models.user import EnterpriseUser
from app.api.dependencies import get_current_user

router = APIRouter(tags=["题库管理"])

AI_BACKEND = "http://127.0.0.1:8001"


@router.post("/questions/import-check", summary="题库导入查重（转发至C端）")
async def proxy_import_check(
    file: UploadFile = File(...),
    current_user: EnterpriseUser = Depends(get_current_user)
):
    async with httpx.AsyncClient(timeout=60.0) as client:
        # 转发文件到 C 端
        resp = await client.post(
            f"{AI_BACKEND}/api/questions/import-check",
            files={"file": (file.filename, await file.read(), file.content_type or "application/json")}
        )
        return resp.json()


@router.post("/questions/import-confirmed", summary="确认导入题目（转发至C端）")
async def proxy_import_confirmed(
    body: dict,
    current_user: EnterpriseUser = Depends(get_current_user)
):
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{AI_BACKEND}/api/questions/import-confirmed",
            json=body
        )
        return resp.json()
