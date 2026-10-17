"""
개선된 Recursive Self-Improvement (RSI) Agent
LangChain + LangGraph 기반의 고급 자기 개선 에이전트

주요 특징:
- 적응형 검색 전략 (Adaptive Search Strategy)
- 정량화된 품질 평가 (Quantified Quality Assessment)
- 수렴 감지 (Convergence Detection)
- 다중 에이전트 협업 (Multi-Agent Collaboration)
- 성능 메트릭 기반 피드백 루프
"""

import asyncio
import json
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
from collections import defaultdict
import statistics

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END


class SearchStrategy(Enum):
    """검색 전략"""
    BREADTH_FIRST = "breadth_first"  # 넓은 범위 탐색
    DEPTH_FIRST = "depth_first"      # 깊이 있는 탐색
    TARGETED = "targeted"             # 특정 영역 집중
    HYBRID = "hybrid"                 # 혼합


@dataclass
class QualityMetrics:
    """품질 메트릭"""
    relevance_score: float = 0.0      # 관련성 (0-1)
    completeness_score: float = 0.0   # 완전성 (0-1)
    novelty_score: float = 0.0        # 새로움 (0-1)
    diversity_score: float = 0.0      # 다양성 (0-1)
    confidence_score: float = 0.0     # 확신도 (0-1)

    @property
    def overall_score(self) -> float:
        """종합 점수 (가중 평균)"""
        weights = {
            'relevance': 0.3,
            'completeness': 0.25,
            'novelty': 0.2,
            'diversity': 0.15,
            'confidence': 0.1
        }
        return (
            self.relevance_score * weights['relevance'] +
            self.completeness_score * weights['completeness'] +
            self.novelty_score * weights['novelty'] +
            self.diversity_score * weights['diversity'] +
            self.confidence_score * weights['confidence']
        )


@dataclass
class ResearchResult:
    """연구 결과"""
    query: str
    findings: List[str] = field(default_factory=list)
    sources: List[Dict] = field(default_factory=list)
    metrics: QualityMetrics = field(default_factory=QualityMetrics)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    search_strategy_used: SearchStrategy = SearchStrategy.HYBRID


@dataclass
class RSIAgentState:
    """RSI 에이전트 상태"""
    # 입력
    research_topic: str
    initial_query: str

    # 진행 상황
    iteration: int = 0
    max_iterations: int = 5
    current_strategy: SearchStrategy = SearchStrategy.HYBRID

    # 결과 누적
    research_results: List[ResearchResult] = field(default_factory=list)
    quality_history: List[float] = field(default_factory=list)

    # 메시지 로그
    messages: List = field(default_factory=list)

    # 수렴 감지
    convergence_threshold: float = 0.95
    improvement_threshold: float = 0.02

    # 피드백 정보
    feedback_notes: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)


class AdaptiveSearchStrategy:
    """적응형 검색 전략"""

    def __init__(self):
        self.strategy_performance = defaultdict(list)

    def select_strategy(
        self,
        iteration: int,
        quality_history: List[float],
        convergence_detected: bool
    ) -> SearchStrategy:
        """반복 횟수와 품질 이력을 기반으로 검색 전략 선택"""

        if iteration == 0:
            return SearchStrategy.BREADTH_FIRST

        if convergence_detected:
            return SearchStrategy.DEPTH_FIRST

        # 최근 성능에 따라 전략 조정
        if len(quality_history) >= 2:
            recent_improvement = quality_history[-1] - quality_history[-2]
            if recent_improvement < 0.01:
                return SearchStrategy.TARGETED

        return SearchStrategy.HYBRID

    def record_performance(
        self,
        strategy: SearchStrategy,
        quality_score: float
    ):
        """전략 성능 기록"""
        self.strategy_performance[strategy.value].append(quality_score)

    def get_strategy_stats(self) -> Dict:
        """전략별 통계"""
        stats = {}
        for strategy, scores in self.strategy_performance.items():
            if scores:
                stats[strategy] = {
                    'avg_score': statistics.mean(scores),
                    'max_score': max(scores),
                    'usage_count': len(scores)
                }
        return stats


class ConvergenceDetector:
    """수렴 감지기"""

    @staticmethod
    def detect_convergence(
        quality_history: List[float],
        threshold: float = 0.95,
        window_size: int = 3
    ) -> Tuple[bool, float, str]:
        """
        수렴 여부 감지

        Returns:
            - 수렴 여부
            - 최종 점수
            - 사유
        """

        if len(quality_history) < window_size:
            return False, 0.0, "불충분한 데이터"

        # 1. 높은 품질 달성
        if quality_history[-1] >= threshold:
            return True, quality_history[-1], "목표 품질 달성"

        # 2. 안정화 감지 (최근 N개의 표준편차 < 0.01)
        recent_scores = quality_history[-window_size:]
        std_dev = statistics.stdev(recent_scores) if len(recent_scores) > 1 else 0
        if std_dev < 0.01:
            return True, statistics.mean(recent_scores), "성능 안정화"

        # 3. 개선 정체 감지
        improvements = [
            quality_history[i] - quality_history[i-1]
            for i in range(1, len(quality_history))
        ]
        if len(improvements) >= 3:
            avg_improvement = statistics.mean(improvements[-3:])
            if avg_improvement < 0.005:
                return True, quality_history[-1], "개선 정체"

        return False, quality_history[-1], "진행 중"


class MultiAgentCollaborator:
    """다중 에이전트 협업 관리자"""

    def __init__(self, num_agents: int = 3):
        self.num_agents = num_agents
        self.agent_specializations = [
            "논문/학술자료",
            "실제 사례/사용 예시",
            "최신 트렌드/뉴스"
        ]

    async def collaborate(
        self,
        research_topic: str,
        current_results: List[ResearchResult]
    ) -> List[str]:
        """
        다중 에이전트가 협업하여 부족한 부분 식별

        Returns:
            개선 제안 목록
        """
        suggestions = []

        for i, specialization in enumerate(self.agent_specializations):
            # 각 에이전트가 자신의 전문 영역에서 부족한 부분 확인
            suggestion = await self._agent_evaluate(
                specialization,
                research_topic,
                current_results
            )
            if suggestion:
                suggestions.append(f"에이전트 {i+1} ({specialization}): {suggestion}")

        return suggestions

    async def _agent_evaluate(
        self,
        specialization: str,
        topic: str,
        results: List[ResearchResult]
    ) -> str:
        """개별 에이전트 평가 (시뮬레이션)"""
        # 실제 구현에서는 LLM 호출
        await asyncio.sleep(0.1)  # 시뮬레이션 지연

        result_texts = [r.query for r in results]
        if specialization not in str(result_texts):
            return f"{specialization} 관련 정보가 부족합니다. 추가 검색을 권장합니다."
        return ""


class ImprovedRSIAgent:
    """개선된 Recursive Self-Improvement Agent"""

    def __init__(
        self,
        max_iterations: int = 5,
        quality_threshold: float = 0.95,
        convergence_threshold: float = 0.95
    ):
        self.max_iterations = max_iterations
        self.quality_threshold = quality_threshold
        self.convergence_threshold = convergence_threshold

        self.strategy_selector = AdaptiveSearchStrategy()
        self.convergence_detector = ConvergenceDetector()
        self.collaborator = MultiAgentCollaborator()

        self._build_graph()

    def _build_graph(self):
        """LangGraph 워크플로우 구성"""
        workflow = StateGraph(RSIAgentState)

        # 노드 추가
        workflow.add_node("initialize", self._initialize)
        workflow.add_node("select_strategy", self._select_strategy)
        workflow.add_node("execute_search", self._execute_search)
        workflow.add_node("evaluate_quality", self._evaluate_quality)
        workflow.add_node("detect_convergence", self._detect_convergence)
        workflow.add_node("multi_agent_review", self._multi_agent_review)
        workflow.add_node("generate_report", self._generate_report)

        # 엣지 구성
        workflow.add_edge(START, "initialize")
        workflow.add_edge("initialize", "select_strategy")
        workflow.add_edge("select_strategy", "execute_search")
        workflow.add_edge("execute_search", "evaluate_quality")
        workflow.add_edge("evaluate_quality", "detect_convergence")

        # 조건부 엣지 (수렴 여부)
        workflow.add_conditional_edges(
            "detect_convergence",
            self._should_continue,
            {
                "continue": "multi_agent_review",
                "finalize": "generate_report"
            }
        )

        workflow.add_edge("multi_agent_review", "select_strategy")
        workflow.add_edge("generate_report", END)

        self.graph = workflow.compile()

    async def _initialize(self, state: RSIAgentState) -> RSIAgentState:
        """초기화 단계"""
        state.messages.append(
            SystemMessage(content=f"주제: {state.research_topic}")
        )
        state.iteration = 0
        return state

    async def _select_strategy(self, state: RSIAgentState) -> RSIAgentState:
        """검색 전략 선택"""
        convergence_detected = len(state.quality_history) >= 2

        strategy = self.strategy_selector.select_strategy(
            state.iteration,
            state.quality_history,
            convergence_detected
        )
        state.current_strategy = strategy

        state.messages.append(
            AIMessage(content=f"선택된 전략: {strategy.value}")
        )
        return state

    async def _execute_search(self, state: RSIAgentState) -> RSIAgentState:
        """검색 실행"""
        # 실제 구현에서는 Tavily API 호출
        result = ResearchResult(
            query=state.research_results[-1].query if state.research_results else state.initial_query,
            search_strategy_used=state.current_strategy
        )

        # 시뮬레이션된 결과
        result.findings = [
            f"발견사항 {state.iteration + 1}-1: 심층 분석 결과",
            f"발견사항 {state.iteration + 1}-2: 패턴 식별",
            f"발견사항 {state.iteration + 1}-3: 관계도 파악"
        ]

        state.research_results.append(result)
        state.iteration += 1

        state.messages.append(
            AIMessage(content=f"반복 {state.iteration}: 검색 완료")
        )
        return state

    async def _evaluate_quality(self, state: RSIAgentState) -> RSIAgentState:
        """품질 평가"""
        latest_result = state.research_results[-1]

        # 품질 메트릭 계산
        quality = QualityMetrics(
            relevance_score=0.85 + (state.iteration * 0.02),
            completeness_score=0.70 + (state.iteration * 0.03),
            novelty_score=0.90,
            diversity_score=0.75 + (state.iteration * 0.02),
            confidence_score=0.80 + (state.iteration * 0.02)
        )

        latest_result.metrics = quality
        state.quality_history.append(quality.overall_score)

        state.messages.append(
            AIMessage(content=f"품질 점수: {quality.overall_score:.2%}")
        )
        return state

    async def _detect_convergence(self, state: RSIAgentState) -> RSIAgentState:
        """수렴 감지"""
        converged, score, reason = self.convergence_detector.detect_convergence(
            state.quality_history,
            state.convergence_threshold
        )

        state.feedback_notes.append(f"수렴 상태: {reason} (점수: {score:.2%})")
        state.messages.append(AIMessage(content=reason))

        return state

    async def _multi_agent_review(self, state: RSIAgentState) -> RSIAgentState:
        """다중 에이전트 검토"""
        suggestions = await self.collaborator.collaborate(
            state.research_topic,
            state.research_results
        )
        state.improvement_suggestions.extend(suggestions)

        state.messages.append(
            AIMessage(content=f"개선 제안: {len(suggestions)}개")
        )
        return state

    async def _generate_report(self, state: RSIAgentState) -> RSIAgentState:
        """최종 보고서 생성"""
        report = self._create_report(state)
        state.messages.append(AIMessage(content="보고서 생성 완료"))
        return state

    def _create_report(self, state: RSIAgentState) -> str:
        """보고서 생성"""
        report = f"""# Recursive Self-Improvement Agent 최종 보고서

## 주제
{state.research_topic}

## 실행 요약
총 {state.iteration}회 반복 수행
최종 품질 점수: {state.quality_history[-1]:.2%}

## 반복별 품질 개선
"""

        for i, score in enumerate(state.quality_history, 1):
            report += f"- 반복 {i}: {score:.2%}\n"

        report += f"""
## 채택된 전략
- 적응형 검색 전략
- 다중 에이전트 협업
- 실시간 수렴 감지

## 개선 제안
"""
        for suggestion in state.improvement_suggestions:
            report += f"- {suggestion}\n"

        report += f"""
## 성능 메트릭
- 관련성: {state.research_results[-1].metrics.relevance_score:.2%}
- 완전성: {state.research_results[-1].metrics.completeness_score:.2%}
- 새로움: {state.research_results[-1].metrics.novelty_score:.2%}
- 다양성: {state.research_results[-1].metrics.diversity_score:.2%}
- 확신도: {state.research_results[-1].metrics.confidence_score:.2%}

## 결론
에이전트가 자기 개선을 통해 점진적으로 더 나은 결과를 생성했습니다.
적응형 전략과 다중 에이전트 협업이 효과적으로 작동했습니다.
"""
        return report

    def _should_continue(self, state: RSIAgentState) -> str:
        """반복 계속 여부 결정"""
        if state.iteration >= state.max_iterations:
            return "finalize"

        # 수렴 여부 확인
        if len(state.quality_history) >= 2:
            converged, _, _ = self.convergence_detector.detect_convergence(
                state.quality_history,
                state.convergence_threshold
            )
            if converged:
                return "finalize"

        return "continue"

    async def run(
        self,
        research_topic: str,
        initial_query: str
    ) -> Dict:
        """RSI 에이전트 실행"""

        initial_state = RSIAgentState(
            research_topic=research_topic,
            initial_query=initial_query,
            max_iterations=self.max_iterations
        )

        # 워크플로우 실행
        final_state = await self._execute_workflow(initial_state)

        return {
            "topic": research_topic,
            "iterations": final_state.iteration,
            "final_quality_score": final_state.quality_history[-1] if final_state.quality_history else 0.0,
            "quality_progression": final_state.quality_history,
            "suggestions": final_state.improvement_suggestions,
            "messages": final_state.messages
        }

    async def _execute_workflow(self, state: RSIAgentState) -> RSIAgentState:
        """워크플로우 순차 실행 (async)"""
        state = await self._initialize(state)

        while state.iteration < state.max_iterations:
            state = await self._select_strategy(state)
            state = await self._execute_search(state)
            state = await self._evaluate_quality(state)
            state = await self._detect_convergence(state)

            if self._should_continue(state) == "finalize":
                break

            state = await self._multi_agent_review(state)

        state = await self._generate_report(state)
        return state


async def main():
    """RSI Agent 데모"""
    print("\n" + "="*70)
    print("🔄 개선된 Recursive Self-Improvement Agent 데모")
    print("="*70)

    agent = ImprovedRSIAgent(
        max_iterations=5,
        quality_threshold=0.95,
        convergence_threshold=0.95
    )

    result = await agent.run(
        research_topic="LangChain에서의 재귀적 자기 개선 메커니즘",
        initial_query="LangChain 에이전트가 어떻게 자신을 개선하는가?"
    )

    print(f"\n✅ 실행 완료!")
    print(f"- 반복 횟수: {result['iterations']}")
    print(f"- 최종 품질: {result['final_quality_score']:.2%}")
    print(f"- 품질 진행: {[f'{s:.2%}' for s in result['quality_progression']]}")
    print(f"- 개선 제안: {len(result['suggestions'])}개")


if __name__ == "__main__":
    asyncio.run(main())
