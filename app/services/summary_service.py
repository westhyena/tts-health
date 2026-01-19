import os
from typing import Optional
from openai import OpenAI


class SummaryService:
    def summarize(self, text: str, method: str = "rule-based") -> str:
        """
        주어진 텍스트를 요약합니다.

        Args:
            text (str): 요약할 원본 텍스트
            method (str): 요약 방식 ('rule-based' 또는 'llm')

        Returns:
            str: 요약된 텍스트
        """
        if not text:
            return ""

        if method == "llm":
            return self._summarize_with_llm(text)
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

    def _summarize_with_llm(self, text: str) -> str:
        """
        LLM API를 호출하여 요약하는 로직을 이곳에 구현합니다.
        예: OpenAI API, Local LLM 등
        """
        # TODO: 실제 LLM API 연동 구현
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "Error: OPENAI_API_KEY environment variable is not set."

        client = OpenAI(api_key=api_key)

        prompt = (
            "다음은 의사와 환자의 대화 내용입니다. "
            "이 내용을 바탕으로 전문적인 의료 기록인 SOAP Note 형식으로 요약해주세요.\n\n"
            "형식:\n"
            "Subjective (주관적 호소): 환자가 느끼는 증상, 호소하는 내용\n"
            "Objective (객관적 소견): 의사가 관찰한 내용, 검사 결과 등\n"
            "Assessment (평가): 진단명 또는 의심되는 질환\n"
            "Plan (계획): 처방, 추후 검사 계획, 생활 습관 지도 등\n\n"
            "지침:\n"
            "- 한국어 대화 내용이니 한국어로 자연스럽게 요약해라.\n"
            "- 전문적인 용어를 사용하되, 내용은 이해하기 쉽게 간결하게 작성해라.\n\n"
            f"대화 내용:\n{text}"
        )

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful medical assistant skilled in creating SOAP notes.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error during LLM summarization: {str(e)}"


summary_service = SummaryService()
