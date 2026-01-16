import os
import time
import logging
from typing import Tuple, List, Dict, Any
from faster_whisper import WhisperModel

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class STTService:
    def __init__(self):
        self.models = {}
        # 기본 디바이스 설정: CUDA를 우선 시도
        self.device = "cuda"
        self.compute_type = "float16"  # CUDA의 경우 float16 권장

        # 간단한 CUDA 확인 (ctranslate2는 별도 라이브러리지만, 로직 상 try-except로 처리)
        # 만약 실제 런타임에 CUDA가 없으면 로딩 시 에러가 발생하므로, 아래 get_model에서 처리

    def get_model(self, model_size: str) -> WhisperModel:
        """
        요청된 사이즈의 모델을 로드하거나 캐시된 모델을 반환합니다.
        CUDA 초기화 실패 시 CPU로 폴백합니다.
        """
        if model_size in self.models:
            return self.models[model_size]

        try:
            logger.info(f"모델 '{model_size}' 로딩 중... Device: {self.device}")
            model = WhisperModel(
                model_size, device=self.device, compute_type=self.compute_type
            )
            # 로딩 성공 시 캐시
            self.models[model_size] = model
            logger.info(f"모델 '{model_size}' 로딩 완료 (Device: {self.device})")
            return model
        except Exception as e:
            logger.warning(f"CUDA 모드로 모델 로딩 실패: {e}. CPU 모드로 전환합니다.")
            self.device = "cpu"
            self.compute_type = "int8"  # CPU에서는 int8 권장

            try:
                model = WhisperModel(
                    model_size, device=self.device, compute_type=self.compute_type
                )
                self.models[model_size] = model
                logger.info(f"모델 '{model_size}' 로딩 완료 (Device: {self.device})")
                return model
            except Exception as cpu_e:
                logger.error(f"CPU 모드로 모델 로딩 실패: {cpu_e}")
                raise cpu_e

    def transcribe(self, audio_path: str, model_size: str = "base") -> Dict[str, Any]:
        """
        오디오 파일을 텍스트로 변환합니다.

        Args:
            audio_path (str): 오디오 파일 경로
            model_size (str): 모델 크기 ('base' or 'small')

        Returns:
            dict: {
                "text": 전체 텍스트,
                "language": 감지된 언어,
                "segments": 세그먼트 상세,
                "processing_time": 소요 시간
            }
        """
        start_time = time.time()

        model = self.get_model(model_size)

        # transcribe 호출
        # beam_size=5 등은 일반적인 정확도 향상 옵션
        segments_generator, info = model.transcribe(audio_path, beam_size=5)

        # segments는 제너레이터이므로 리스트로 변환하며 텍스트 추출
        segments = []
        full_text_list = []

        for segment in segments_generator:
            full_text_list.append(segment.text)
            segments.append(
                {"start": segment.start, "end": segment.end, "text": segment.text}
            )

        processing_time = time.time() - start_time
        full_text = " ".join(full_text_list).strip()

        return {
            "text": full_text,
            "language": info.language,
            "segments": segments,
            "processing_time": processing_time,
        }


# 싱글톤 인스턴스처럼 사용하기 위해 객체 생성 (필요 시 의존성 주입으로 변경 가능)
stt_service = STTService()
