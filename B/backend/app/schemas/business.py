# app/schemas/business.py
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class JobCreateReq(BaseModel):
    title: str
    department: Optional[str] = None
    difficulty: str = "Medium"
    max_participants: Optional[int] = 50
    cmci_value: Optional[float] = 0.75
    rag_id: Optional[str] = None

