import requests
import time
import os
import sys


def upload_audio_file(
    file_path: str,
    server_url: str = "http://localhost:8000/upload-audio",
    max_retries: int = 3,
):
    """
    오디오 파일을 서버에 업로드하고 STT 및 요약 결과를 받아옵니다.
    네트워크 오류 시 간단한 재시도 로직이 포함되어 있습니다.
    """
    if not os.path.exists(file_path):
        print(f"[Error] 파일이 존재하지 않습니다: {file_path}")
        return

    file_name = os.path.basename(file_path)
    print(f"--- ['{file_name}' 업로드 시작] ---")

    for attempt in range(1, max_retries + 1):
        try:
            print(
                f"[{attempt}/{max_retries}] 서버로 파일 전송 중... (URL: {server_url})"
            )

            # 파일 열기 및 전송
            with open(file_path, "rb") as f:
                files = {
                    "file": (file_name, f, "audio/wav")
                }  # MIME type은 파일에 맞춰 조정 가능
                data = {"model_size": "base"}  # 필요 시 'small'로 변경 가능

                # 타임아웃 설정 (서버 처리 시간 감안하여 넉넉하게 60초)
                response = requests.post(server_url, files=files, data=data, timeout=60)

            # 응답 상태 코드 확인
            response.raise_for_status()

            # 결과 파싱
            result = response.json()

            print("\n[업로드 및 처리 성공!]")
            print("=" * 50)
            print(f"▶ 언어: {result.get('language')}")
            print(f"▶ 처리 시간: {result.get('processing_time'):.2f}초")
            print("-" * 50)
            print("[STT 결과]")
            print(result.get("text"))
            print("-" * 50)
            print("[요약 결과]")
            print(result.get("summary"))
            print("=" * 50)

            return result

        except requests.exceptions.ConnectionError:
            print(
                f"[Warning] 서버 연결 실패. 잠시 후 재시도합니다... ({attempt}/{max_retries})"
            )
            time.sleep(2)  # 재시도 대기
        except requests.exceptions.Timeout:
            print(
                f"[Warning] 서버 응답 시간 초과. 잠시 후 재시도합니다... ({attempt}/{max_retries})"
            )
            time.sleep(2)
        except requests.exceptions.HTTPError as e:
            print(f"[Error] 서버 에러 발생: {e}")
            # 4xx 에러 등은 재시도해도 실패할 가능성이 높으므로 중단할 수도 있지만, 여기선 루프 진행 여부 결정
            if 400 <= response.status_code < 500:
                print("클라이언트 요청 오류로 인해 중단합니다.")
                break
            time.sleep(2)
        except Exception as e:
            print(f"[Error] 알 수 없는 오류 발생: {e}")
            break

    print("\n[Failed] 최대 재시도 횟수를 초과했거나 오류로 인해 실패했습니다.")


if __name__ == "__main__":
    # 테스트용 샘플 파일 경로 (실제 파일 경로로 변경 필요)
    # 예: "test_audio.wav" 파일이 같은 디렉토리에 있다고 가정
    sample_audio_path = "test_audio.wav"

    # 사용자가 인자로 파일 경로를 주면 그것을 사용
    if len(sys.argv) > 1:
        sample_audio_path = sys.argv[1]

    # 파일이 없으면 더미 파일 생성 (테스트용) - 실제 오디오 데이터가 아니면 에러날 수 있음
    if not os.path.exists(sample_audio_path):
        print(f"주의: '{sample_audio_path}' 파일을 찾을 수 없습니다.")
        print("실제 테스트를 위해 유효한 .wav 또는 .m4a 파일 경로를 인자로 넘겨주세요.")
        print("예: python client_test.py /path/to/my_recording.wav")
    else:
        upload_audio_file(sample_audio_path)
