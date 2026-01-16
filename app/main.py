from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import shutil
import os
import uuid
import logging
from app.services.stt_service import stt_service
from app.services.summary_service import summary_service
from app.schemas import STTResponse

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="STT & Summary API",
    description="Faster-Whisper 기반 STT 및 요약 API 서버",
    version="1.0.0",
)

# Static file settings
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 임시 파일 저장 경로
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/upload-audio", response_model=STTResponse)
async def upload_audio(
    file: UploadFile = File(...),
    model_size: str = Form(
        "base", description="사용할 STT 모델 크기 ('base' 또는 'small')"
    ),
):
    """
    오디오 파일을 업로드하여 텍스트로 변환(STT)하고 요약을 생성합니다.

    - **file**: .wav 또는 .m4a 음성 파일
    - **model_size**: 'base' (기본값) 또는 'small' 선택 가능
    """

    # 지원하는 파일 확장자 확인
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    if ext not in [".wav", ".m4a", ".mp3", ".webm"]:  # mp3, webm 추가
        raise HTTPException(
            status_code=400,
            detail="지원되지 않는 파일 형식입니다. (.wav, .m4a, .mp3, .webm 만 허용)",
        )

    # 고유한 파일명 생성하여 저장 (동시 요청 충돌 방지)
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        # 1. 파일 저장
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"파일 저장 완료: {file_path}")

        # 2. STT 처리
        # model_size 유효성 검사는 stt_service 내부 혹은 여기서 간단히 처리 가능
        if model_size not in ["base", "small"]:
            # 요청사항에는 'base' 또는 'small'을 선택할 수 있게 해달라고 했으므로 강제하거나 에러 처리
            # 여기서는 편의상 base로 fallback하거나 에러를 낼 수 있음. 에러 처리:
            raise HTTPException(
                status_code=400, detail="model_size는 'base' 또는 'small'이어야 합니다."
            )

        logger.info(f"STT 변환 시작 (Modelsize: {model_size})")
        stt_result = stt_service.transcribe(file_path, model_size=model_size)

        # 3. 요약 처리
        full_text = stt_result["text"]
        logger.info("요약 생성 시작")
        summary_text = summary_service.summarize(full_text, method="rule-based")

        # 4. 응답 생성
        response = STTResponse(
            text=full_text,
            summary=summary_text,
            language=stt_result["language"],
            processing_time=stt_result["processing_time"],
            segments=stt_result["segments"],
        )

        return response

    except Exception as e:
        logger.error(f"처리 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # 5. 임시 파일 정리
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"임시 파일 삭제 완료: {file_path}")


@app.get("/")
async def read_index():
    return FileResponse("app/static/index.html")
