# app/api/v1/jobs.py
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...core.datebase import get_db
from ...core.config import get_env
from ...models.business import JobPosition
from ...models.user import EnterpriseUser
from ...schemas.business import JobCreateReq
from ...api.dependencies import get_current_user

router = APIRouter(prefix="/jobs", tags=["企业发布面试"])

# C端部署的地址（前端地址）
C_END_FRONTEND_URL = get_env("C_END_URL", "http://localhost:5173")


@router.post("")
def create_job(job_in: JobCreateReq, db: Session = Depends(get_db),
               current_user: EnterpriseUser = Depends(get_current_user)):
    unique_token = str(uuid.uuid4())
    # 1. 存入数据库
    new_job = JobPosition(
        enterprise_id=current_user.id,
        title=job_in.title,
        department=job_in.department,
        token=unique_token,
        difficulty=job_in.difficulty,
        max_participants=job_in.max_participants,
        cmci_value=job_in.cmci_value,
        rag_id=job_in.rag_id,
        status="open",
        created_at=datetime.now()

    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    # 2. 生成带 job_id 和 title 的专属 C端面试链接
    # 前端拿着这个链接发给候选人，候选人点开就会带上这些参数
    invitation_link = f"{C_END_FRONTEND_URL}/start?token={new_job.token}"

    return {
        "status": "success",
        "job_id": new_job.id,
        "token": unique_token,
        "invitation_link": invitation_link,
        "created_at": new_job.created_at
    }

@router.get("")
def list_jobs(db: Session = Depends(get_db),
              current_user: EnterpriseUser = Depends(get_current_user)):
    """获取当前企业所有岗位"""
    jobs = db.query(JobPosition).filter(
        JobPosition.enterprise_id == current_user.id
    ).order_by(JobPosition.created_at.desc()).all()

    return {
        "status": "success",
        "jobs": [
            {
                "id": j.id,
                "title": j.title,
                "department": j.department,
                "difficulty": j.difficulty,
                "status": j.status,
                "token": j.token,
                "max_participants": j.max_participants,
                "cmci_value": j.cmci_value,
                "rag_id": j.rag_id,
                "invitation_link": f"{C_END_FRONTEND_URL}/start?token={j.token}",
                "created_at": str(j.created_at) if j.created_at else None
            }
            for j in jobs
        ]
    }
