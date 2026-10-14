"""
Deep Search 메인 애플리케이션
에이전트 기반 검색 시스템의 진입점
"""

import asyncio
import json
from typing import Optional
from llm_client import (
    LLMClient,
    SupervisorAgent,
    ResearcherAgent,
    CompressionAgent,
    ReportGenerator
)
from search_tools import SearchManager, SearchToolInterface
from config import config


class DeepSearchEngine:
    """통합 Deep Search 엔진"""

    def __init__(
        self,
        search_backend: str = "tavily",
        api_key: Optional[str] = None
    ):
        # LLM 클라이언트
        self.llm = LLMClient(api_key)

        # 검색 도구
        self.search_manager = SearchManager(
            backend=search_backend,
            api_key=config.tavily_api_key
        )
        self.search_tools = SearchToolInterface(self.search_manager)

        # 에이전트들
        self.supervisor = SupervisorAgent(self.llm)
        self.researcher = ResearcherAgent(self.llm, self.search_tools)
        self.compressor = CompressionAgent(self.llm)
        self.reporter = ReportGenerator(self.llm)

        # 상태
        self.notes = []
        self.raw_notes = []

    async def search(self, topic: str, verbose: bool = True) -> dict:
        """
        메인 검색 메서드

        Args:
            topic: 검색 주제
            verbose: 단계별 로그 출력

        Returns:
            {
                "topic": str,
                "research_brief": dict,
                "notes": list,
                "compressed": dict,
                "report": str,
                "search_history": list
            }
        """

        if verbose:
            print(f"\n🔍 Deep Search 시작: {topic}\n")

        # Step 1: 사용자 입력 명확화
        if verbose:
            print("📋 Step 1: 입력 명확화...")
        research_brief = self._clarify_request(topic)
        if verbose:
            print(f"✓ 리서치 브리프: {json.dumps(research_brief, ensure_ascii=False, indent=2)}\n")

        # Step 2-N: 반복 연구 사이클
        iteration = 0
        while iteration < config.max_supervisor_iterations:
            iteration += 1
            if verbose:
                print(f"🔄 반복 {iteration}/{config.max_supervisor_iterations}")

            # Step 2: 감독자가 연구 계획 수립
            if verbose:
                print("👔 Step 2: 감독자가 연구 계획 수립...")
            tasks = self.supervisor.plan_research(
                json.dumps(research_brief, ensure_ascii=False)
            )

            if verbose:
                print(f"✓ 계획된 작업: {len(tasks.get('tasks', []))} 개\n")

            # Step 3: 병렬 연구 실행
            if verbose:
                print("🔬 Step 3: 연구원들이 병렬 검색 실행...")

            research_tasks = [
                self.researcher.conduct_research(task["query"])
                for task in tasks.get("tasks", [])[:config.max_concurrent_researchers]
            ]

            results = await asyncio.gather(*research_tasks)

            # 결과 수집
            for result in results:
                if result:
                    self.raw_notes.append(result)
                    # 분석 결과만 notes에 저장
                    self.notes.append({
                        "query": result["query"],
                        "summary": result["analysis"][:500]  # 요약
                    })

            if verbose:
                print(f"✓ {len(results)} 개 연구 결과 수집\n")

            # Step 4: 결과 평가 및 종료 판단
            if verbose:
                print("🎯 Step 4: 감독자가 결과 평가...")

            evaluation = self.supervisor.evaluate_results(
                [str(n) for n in self.notes],
                iteration,
                config.max_supervisor_iterations
            )

            if verbose:
                print(f"✓ 신뢰도: {evaluation.get('confidence', 0):.1%}")
                print(f"✓ 충분성: {'YES' if evaluation.get('is_sufficient') else 'NO'}\n")

            # 충분하거나 최대 반복에 도달하면 종료
            if evaluation.get("is_sufficient") or iteration >= config.max_supervisor_iterations:
                if verbose:
                    print("✅ 리서치 완료, 보고서 생성으로 이동\n")
                break

        # Step 5: 정보 압축
        if verbose:
            print("📦 Step 5: 정보 압축 및 최적화...")

        compressed = self.compressor.compress(self.raw_notes)
        if verbose:
            print(f"✓ 핵심 발견: {len(compressed.get('key_findings', []))} 개\n")

        # Step 6: 최종 보고서 생성
        if verbose:
            print("📄 Step 6: 최종 보고서 생성...")

        report = self.reporter.generate(
            topic,
            self.notes,
            compressed
        )

        if verbose:
            print(f"✓ 보고서 생성 완료 ({len(report)} 자)\n")

        # 결과 반환
        return {
            "topic": topic,
            "research_brief": research_brief,
            "notes": self.notes,
            "compressed": compressed,
            "report": report,
            "search_history": self.search_tools.get_search_history(),
            "iterations": iteration
        }

    def _clarify_request(self, topic: str) -> dict:
        """사용자 입력 명확화"""

        prompt = f"""사용자의 리서치 요청을 명확히 하세요:

요청: {topic}

다음 JSON을 반환하세요:
{{
  "main_topic": "주제",
  "research_questions": ["질문1", "질문2", "질문3"],
  "scope": "범위 (broad/focused/specific)",
  "expected_depth": "깊이 (basic/intermediate/expert)"
}}"""

        return self.llm.call_json(prompt)


async def main():
    """메인 실행 함수"""

    # Deep Search 엔진 초기화
    engine = DeepSearchEngine(
        search_backend=config.search_backend,
        api_key=config.anthropic_api_key
    )

    # 테스트 주제
    test_topic = "2024년 AI 에이전트 기술 발전 현황과 LangChain의 역할"

    # 검색 실행
    result = await engine.search(test_topic, verbose=True)

    # 결과 출력
    print("=" * 80)
    print("📊 최종 보고서")
    print("=" * 80)
    print(result["report"])

    print("\n" + "=" * 80)
    print("📈 통계")
    print("=" * 80)
    print(f"• 총 반복: {result['iterations']}")
    print(f"• 수집된 노트: {len(result['notes'])}")
    print(f"• 핵심 발견: {len(result['compressed'].get('key_findings', []))}")
    print(f"• 검색 횟수: {len(result['search_history'])}")

    return result


if __name__ == "__main__":
    # 비동기 실행
    result = asyncio.run(main())

    # 선택사항: 결과를 파일에 저장
    with open("search_result.json", "w", encoding="utf-8") as f:
        json.dump({
            "topic": result["topic"],
            "iterations": result["iterations"],
            "key_findings": result["compressed"].get("key_findings", []),
            "confidence": result["compressed"].get("confidence_score", 0)
        }, f, ensure_ascii=False, indent=2)

    print("\n✅ 결과가 search_result.json에 저장되었습니다.")
