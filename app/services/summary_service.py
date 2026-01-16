from typing import Optional


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
        return (
            "[LLM 요약 기능은 아직 구현되지 않았습니다. API Key 설정이 필요합니다.] "
            + text[:100]
            + "..."
        )


summary_service = SummaryService()
