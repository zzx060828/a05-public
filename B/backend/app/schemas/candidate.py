# app/schemas/candidate.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ---------------- 候选人列表相关 Schema ----------------

class CandidateItem(BaseModel):
    record_id: int = Field(..., alias="id", description="面试记录唯一ID")
    job_id: int
    candidate_name: str
    candidate_phone: Optional[str] = None
    match_score: float = Field(..., description="综合匹配度得分 (0-100)")
    status: str = Field(..., description="状态: 面试中 / 已完成 / 已出报告")
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class CandidateListResponse(BaseModel):
    total: int = Field(..., description="总条数")
    page: int
    page_size: int
    items: List[CandidateItem]


# ---------------- 面试报告解析相关 Schema ----------------

class CandidateReportDetailResponse(BaseModel):
    record_id: int
    job_id: int
    candidate_name: str
    match_score: float

    # 解析 C 端 JSON 数据大包 (来自 full_report_data)
    summary_packet: Dict[str, Any] = Field(default_factory=dict, description="综合评语与优势总结")
    radar_packet: Dict[str, Any] = Field(default_factory=dict,
                                         description="维度雷达图数据 (如技术契合、逻辑推演、沟通表达)")
    content_items: List[Dict[str, Any]] = Field(default_factory=list, description="逐题回答、评价及得分细节")
    report_markdown: str = Field("", description="完整的 Markdown 格式综合总结报告")
    voice_data: List[Dict[str, Any]] = Field(default_factory=list,
                                             description="多模态声学分析 (语速/停顿/结巴/情绪分布)")
    video_data: List[Dict[str, Any]] = Field(default_factory=list, description="视觉/表情与动作控制数据")
    tips_data: List[Dict[str, Any]] = Field(default_factory=list, description="提升建议与相关学习资源")