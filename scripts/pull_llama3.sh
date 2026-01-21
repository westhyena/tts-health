#!/bin/bash

# Ollama가 설치되어 있는지 확인합니다.
if ! command -v ollama &> /dev/null; then
    echo "오류: Ollama가 설치되어 있지 않습니다."
    echo "먼저 Ollama를 설치해주세요."
    echo "설치 방법: https://ollama.com 에서 다운로드하거나 'brew install ollama'를 실행하세요."
    exit 1
fi

echo "Ollama가 설치되어 있습니다."

# Ollama 서버 상태 확인
if ! ollama list &> /dev/null; then
    echo "알림: Ollama 서버가 실행 중이지 않은 것 같습니다."
    echo "백그라운드에서 'ollama serve'를 시작합니다..."
    
    # 백그라운드에서 서버 시작
    ollama serve > /dev/null 2>&1 &
    ServerPID=$!
    
    echo "서버 시작 대기 중 (5초)..."
    sleep 5
    
    # 다시 확인
    if ! ollama list &> /dev/null; then
        echo "오류: Ollama 서버를 자동으로 시작할 수 없습니다."
        echo "새 터미널 창을 열고 'ollama serve'를 실행한 뒤, 이 스크립트를 다시 실행해주세요."
        # 백그라운드 프로세스가 살아있다면 정리
        kill $ServerPID 2>/dev/null
        exit 1
    fi
fi

echo "Llama 3.1 8B 모델 다운로드를 시작합니다..."
# Llama 3.1 모델을 다운로드합니다.
ollama pull llama3.1

if [ $? -eq 0 ]; then
    echo "모델 다운로드가 성공적으로 완료되었습니다."
else
    echo "모델 다운로드 중 오류가 발생했습니다."
    exit 1
fi
