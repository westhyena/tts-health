import os
from typing import Optional
from openai import OpenAI


class SummaryService:
    def summarize(
        self, text: str, method: str = "rule-based", custom_prompt: Optional[str] = None
    ) -> str:
        """
        주어진 텍스트를 요약합니다.

        Args:
            text (str): 요약할 원본 텍스트
            method (str): 요약 방식 ('rule-based' 또는 'llm')
            custom_prompt (str, optional): LLM 요약 시 사용할 커스텀 프롬프트

        Returns:
            str: 요약된 텍스트
        """
        if not text:
            return ""

        if method == "llm":
            return self._summarize_with_llm(text, custom_prompt)
        else:
            return self._summarize_rule_based(text)

    def _summarize_rule_based(self, text: str) -> str:
        """
        간단한 규칙 기반 요약:
        텍스트가 길 경우 앞의 3문장만 추출하여 요약으로 간주합니다.
        """
        # 문장 분리 (단순히 온점 기준)
        sentences = [s.strip() for s in text.split(".") if s.strip()]

        if len(sentences) <= 3:
            return text

        # 상위 3문장 결합
        summary = ". ".join(sentences[:3]) + "."
        return summary

    def _summarize_with_llm(
        self, text: str, custom_prompt: Optional[str] = None
    ) -> str:
        """
        LLM API를 호출하여 요약하는 로직을 이곳에 구현합니다.
        예: OpenAI API, Local LLM 등
        """
        # TODO: 실제 LLM API 연동 구현
        # LLM Provider 확인 (기본값: openai)
        llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()

        # API Key 설정 (Ollama는 dummy 키 허용)
        api_key = os.getenv("OPENAI_API_KEY")

        client_args = {}
        model_name = "gpt-3.5-turbo"

        if llm_provider == "ollama":
            # Ollama 설정
            # 외부 Ollama 서버 주소 지원 (기본값: localhost)
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
            client_args["base_url"] = base_url
            client_args["api_key"] = (
                "ollama"  # Ollama requires a dummy key compliant with OpenAI SDK
            )
            model_name = "llama3.1"
        else:
            # OpenAI 설정
            if not api_key:
                return "Error: OPENAI_API_KEY environment variable is not set."
            client_args["api_key"] = api_key

        try:
            import logging

            logger = logging.getLogger(__name__)
            logger.info(
                f"Using LLM Provider: {llm_provider.upper()}, Model: {model_name}"
            )

            client = OpenAI(**client_args)

            if custom_prompt:
                template = custom_prompt
            else:
                # 프롬프트 파일 경로 설정 (app/prompts/soap_summary_template.txt)
                base_dir = os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__))
                )  # app/
                prompt_path = os.path.join(
                    base_dir, "prompts", "soap_summary_template.txt"
                )

                try:
                    with open(prompt_path, "r", encoding="utf-8") as f:
                        template = f.read()
                except Exception as e:
                    return f"Error reading prompt file: {str(e)}"

            # Remove the placeholder if present to clean up system prompt
            system_prompt = template.replace("{text}", "").strip()

            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                temperature=0.5,
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Error during LLM summarization ({llm_provider}): {str(e)}"


summary_service = SummaryService()
