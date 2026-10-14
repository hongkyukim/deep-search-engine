"""
LLM (Anthropic Claude) 클라이언트 통합
"""

import json
import re
from typing import Optional
from anthropic import Anthropic
from config import config


class LLMClient:
    """Anthropic Claude API 클라이언트"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.anthropic_api_key
        self.client = Anthropic(api_key=self.api_key)
        self.conversation_history = []

    def call(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> str:
        """LLM API 호출"""

        if model is None:
            model = config.supervisor_model

        try:
            messages = [{"role": "user", "content": prompt}]

            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "당신은 전문적인 리서치 어시스턴트입니다.",
                messages=messages
            )

            result = response.content[0].text

            # 대화 이력에 추가
            self.conversation_history.append({
                "role": "user",
                "content": prompt
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": result
            })

            return result

        except Exception as e:
            return f"[LLM Error: {str(e)}]"

    def call_json(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 4096
    ) -> dict:
        """JSON 응답 기대하는 LLM 호출"""

        if model is None:
            model = config.supervisor_model

        response = self.call(
            prompt=f"{prompt}\n\nJSON 형식으로만 응답하세요.",
            model=model,
            max_tokens=max_tokens,
            temperature=0.3  # JSON은 낮은 temperature
        )

        try:
            # JSON 추출 (마크다운 코드블록 포함 가능)
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            else:
                return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON", "raw_response": response}

    def clear_history(self):
        """대화 이력 초기화"""
        self.conversation_history = []


class SupervisorAgent:
    """감독자 에이전트"""

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.task_queue = []

    def plan_research(self, research_brief: str) -> dict:
        """리서치 계획 수립"""

        prompt = f"""당신은 Research Supervisor입니다.

리서치 브리프:
{research_brief}

이를 바탕으로 3-5개의 구체적인 연구 질문을 생성하세요.
각 질문은 다른 각도에서 주제를 탐색해야 합니다.

JSON 형식:
{{
  "tasks": [
    {{"id": 1, "query": "질문1", "priority": "high"}},
    {{"id": 2, "query": "질문2", "priority": "medium"}}
  ],
  "strategy": "전체 전략 설명"
}}"""

        return self.llm.call_json(prompt)

    def evaluate_results(self, notes: list, current_iteration: int, max_iterations: int) -> dict:
        """연구 결과 평가"""

        prompt = f"""당신은 Research Supervisor입니다.

현재 수집된 정보:
{chr(10).join(notes[:5])}

현재: {current_iteration}/{max_iterations} 반복

다음을 판단하세요:
1. 현재 정보가 충분한가?
2. 추가 연구가 필요한가?
3. 어떤 부분이 더 필요한가?

JSON 형식:
{{
  "is_sufficient": true/false,
  "confidence": 0.0-1.0,
  "next_steps": ["단계1", "단계2"],
  "reasoning": "판단 이유"
}}"""

        return self.llm.call_json(prompt)


class ResearcherAgent:
    """연구원 에이전트"""

    def __init__(self, llm_client: LLMClient, search_tools):
        self.llm = llm_client
        self.search_tools = search_tools

    async def conduct_research(self, query: str) -> dict:
        """연구 실행"""

        # Step 1: 검색
        search_result = await self.search_tools.search(query, num_results=5)

        # Step 2: 결과 분석
        analysis = self._analyze_results(query, search_result["results"])

        return {
            "query": query,
            "search_results": search_result["results"],
            "analysis": analysis
        }

    def _analyze_results(self, query: str, results: list) -> str:
        """검색 결과 분석"""

        results_text = "\n".join([
            f"- {r['title']}: {r['content'][:200]}..."
            for r in results[:3]
        ])

        prompt = f"""검색 질문: {query}

검색 결과:
{results_text}

이 결과들을 분석하여 핵심 발견사항을 정리하세요.
원본 정보는 최대한 보존하되, 명확한 구조로 정리하세요."""

        return self.llm.call(prompt, temperature=0.5)


class CompressionAgent:
    """압축 에이전트 - 정보 최적화"""

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def compress(self, raw_notes: list) -> dict:
        """정보 압축 및 정리"""

        notes_text = "\n".join(str(n) for n in raw_notes[:10])

        prompt = f"""다음 원본 리서치 노트를 정리하세요:

{notes_text}

주의: 정보를 요약하지 말고, 중복을 제거하고 구조화하세요.
원본 정보와 출처는 반드시 보존하세요.

JSON 형식:
{{
  "key_findings": ["발견1", "발견2", "발견3"],
  "sources": [
    {{"title": "제목", "relevance": "high/medium/low"}},
  ],
  "gaps": "추가 정보가 필요한 부분",
  "confidence_score": 0.85
}}"""

        return self.llm.call_json(prompt)


class ReportGenerator:
    """최종 보고서 생성"""

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def generate(self, topic: str, notes: list, compressed_data: dict) -> str:
        """최종 보고서 생성"""

        key_findings = "\n".join([f"- {f}" for f in compressed_data.get("key_findings", [])])

        prompt = f"""당신은 전문적인 리서치 보고서 작성자입니다.

주제: {topic}

핵심 발견사항:
{key_findings}

수집된 정보를 바탕으로 다음 구조의 전문적 마크다운 보고서를 작성하세요:

# {topic}

## Executive Summary
(2-3문장 요약)

## Key Findings
(발견사항 상세)

## Detailed Analysis
(심층 분석)

## Sources
(출처 목록)

## Limitations
(정보 부족 영역)

마크다운 형식으로만 출력하세요."""

        return self.llm.call(prompt, max_tokens=8192, temperature=0.5)
