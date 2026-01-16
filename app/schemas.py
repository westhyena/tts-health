from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class STTResponse(BaseModel):
    """
    STT 및 요약 결과에 대한 응답 스키마입니다.
    """
    text: str = Field(..., description="변환된 전체 텍스트")
    summary: str = Field(..., description="요약된 텍스트")
    language: str = Field(..., description="감지된 언어 (예: 'ko', 'en')")
    processing_time: float = Field(..., description="처리 소요 시간 (초 단위)")
    segments: Optional[List[Dict[str, Any]]] = Field(None, description="세그먼트별 상세 정보 (시작/종료 시간, 텍스트 등)")
