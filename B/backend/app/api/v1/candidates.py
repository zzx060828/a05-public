# app/api/v1/candidates.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
import json


from ...models.business import JobPosition, InterviewRecord,  InterviewReport, User
from ...models.user import EnterpriseUser
from ...schemas.candidate import CandidateListResponse, CandidateItem, CandidateReportDetailResponse
from ...api.dependencies import get_current_user

from ...core.datebase import get_db
router = APIRouter(tags=["候选人看板与报告解析"])


# =========================================================================
# 6. 获取某岗位的面试者列表 (支持真分页与状态过滤)
# =======================================================================
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

@router.get(
    "/jobs/{job_id}/candidates",
    summary="获取某岗位的候选人列表"
)
def get_job_candidates(
        job_id: int,
        page: int = Query(1, ge=1, description="当前页码"),
        page_size: int = Query(10, ge=1, le=100, description="每页条数"),
        db: Session = Depends(get_db),
        current_user: EnterpriseUser = Depends(get_current_user)
):
    # 1. 鉴权：检查该 Job 是否属于当前登录的企业
    job = db.query(JobPosition).filter(
        JobPosition.id == job_id,
        JobPosition.enterprise_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="未找到该岗位或无权访问")

    # 2. 查询 InterviewReport 表
    query = db.query(InterviewReport).filter(InterviewReport.job_id == job_id)

    # 3. 计算总数并分页查询
    total = query.count()
    offset = (page - 1) * page_size
    reports = query.order_by(InterviewReport.generated_at.desc()).offset(offset).limit(page_size).all()

    # 4. 组装候选人列表项
    items = []
    for r in reports:
        # 从 User 表查询真实姓名 (username)
        candidate_name = f"候选人_{r.user_id}"
        if r.user_id:
            user_obj = db.query(User).filter(User.id == r.user_id).first()
            if user_obj and user_obj.username:
                candidate_name = user_obj.username

        # 🌟 核心：获取 score（优先取数据库字段 r.score，如果没有则从 JSON 内容中降级获取）
        score = getattr(r, "score", None)
        if score is None:
            try:
                content = json.loads(r.report_content) if isinstance(r.report_content, str) else (r.report_content or {})
                score = content.get("average_score", content.get("match_score", content.get("summary_packet", {}).get("averageScore", content.get("summary_packet", {}).get("matchScore", 0.0))))
            except Exception:
                score = 0.0

        items.append({
            "record_id": r.id,
            "candidate_name": candidate_name,
            "score": score,                    # 👈 返回给前端列表的匹配得分
            "generated_at": r.generated_at
        })

    return {
        "title": getattr(job, "title", ""),
        "department": getattr(job, "department", ""),
        "max_participants": getattr(job, "max_participants", 0),
        "created_at": getattr(job, "created_at", None),
        "cmci_value": getattr(job, "cmci_value", None),
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    }
# =========================================================================
# 7. 获取单人全量 AI 解析面试报告
# =========================================================================
@router.get(
    "/records/{record_id}/report",
    response_model=CandidateReportDetailResponse,
    summary="获取候选人 AI 面试全量报告"
)
def get_candidate_report(
        record_id: int,
        db: Session = Depends(get_db),
        current_user: EnterpriseUser = Depends(get_current_user)
):
    # 1. 查询 InterviewReport 主记录
    report = db.query(InterviewReport).filter(InterviewReport.id == record_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="面试报告不存在或尚未生成")

    # 2. 校验企业操作权限
    job = db.query(JobPosition).filter(
        JobPosition.id == report.job_id,
        JobPosition.enterprise_id == current_user.id
    ).first()
    if not job:
        raise HTTPException(status_code=403, detail="无权查看此候选人的面试报告")

    # 3. 从 User 表读出对应的 username 作为名字
    candidate_name = f"候选人_{report.user_id}"
    if report.user_id:
        user_obj = db.query(User).filter(User.id == report.user_id).first()
        if user_obj and user_obj.username:
            candidate_name = user_obj.username

    # 4. 🌟 核心：获取 score（优先取数据库字段 report.score，没有则从 JSON 或 Markdown 文本中提取）
    score = getattr(report, "score", None)

    # 解析 report_content 里的 JSON 包
    raw_data = report.report_content
    if isinstance(raw_data, str):
        try:
            raw_data = json.loads(raw_data)
        except Exception:
            raw_data = {}

    if score is None:
        score = (
                raw_data.get("average_score") or
                raw_data.get("summary_packet", {}).get("averageScore") or
                raw_data.get("match_score") or
                raw_data.get("summary_packet", {}).get("matchScore") or
                0
        )

    # 5. 组装并透传回 Response 模型
    return CandidateReportDetailResponse(
        record_id=report.id,
        job_id=report.job_id,
        candidate_name=candidate_name,
        match_score=score,
        summary_packet=raw_data.get("summary_packet", {}),
        radar_packet=raw_data.get("radar_packet", {}),
        content_items=raw_data.get("content_items", []),
        report_markdown=raw_data.get("report_markdown", raw_data.get("summary", "")),
        voice_data=raw_data.get("voice_data", []),
        video_data=raw_data.get("video_data", []),
        tips_data=raw_data.get("tips_data", [])
    )
