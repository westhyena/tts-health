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
    segments: Optional[List[Dict[str, Any]]] = Field(
        None, description="세그먼트별 상세 정보 (시작/종료 시간, 텍스트 등)"
    )


from datetime import date, datetime

# --- EMR Schemas ---


# Patient
class PatientBase(BaseModel):
    name: str
    dob: date
    gender: str


class PatientCreate(PatientBase):
    pass


class Patient(PatientBase):
    id: int

    class Config:
        from_attributes = True


# Doctor
class DoctorBase(BaseModel):
    name: str
    department: str


class DoctorCreate(DoctorBase):
    pass


class Doctor(DoctorBase):
    id: int

    class Config:
        from_attributes = True


# VitalSign
class VitalSignBase(BaseModel):
    systolic: int
    diastolic: int
    heart_rate: int
    temperature: float
    resp_rate: int


class VitalSignCreate(VitalSignBase):
    pass


class VitalSign(VitalSignBase):
    id: int
    visit_id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# Diagnosis
class DiagnosisBase(BaseModel):
    icd_code: str
    display_name: str


class DiagnosisCreate(DiagnosisBase):
    pass


class Diagnosis(DiagnosisBase):
    id: int
    visit_id: int

    class Config:
        from_attributes = True


# Medication
class MedicationBase(BaseModel):
    drug_name: str
    dosage: str
    frequency: str


class MedicationCreate(MedicationBase):
    pass


class Medication(MedicationBase):
    id: int
    visit_id: int

    class Config:
        from_attributes = True


# Note
class NoteBase(BaseModel):
    content: str
    author_id: int


class NoteCreate(NoteBase):
    pass


class Note(NoteBase):
    id: int
    visit_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Visit
class VisitBase(BaseModel):
    doctor_id: int
    department: Optional[str] = None
    visit_date: Optional[datetime] = None
    status: str = "completed"
    chief_complaint: Optional[str] = None


class VisitCreate(VisitBase):
    patient_id: int


class Visit(VisitBase):
    id: int
    patient_id: int
    vitals: List[VitalSign] = []
    diagnoses: List[Diagnosis] = []
    medications: List[Medication] = []
    notes: List[Note] = []

    class Config:
        from_attributes = True
