"""
LangGraph 기반 Deep Search 워크플로우
감독자(Supervisor) ↔ 연구원(Researcher) 패턴
"""

from typing import Optional
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage
from state import AgentState, SupervisorState, ResearcherState
from config import config
from prompts import PROMPTS
from search_tools import SearchToolInterface, SearchManager


class DeepSearchGraph:
    """Deep Search 워크플로우 구현"""

    def __init__(self):
        self.graph_builder = StateGraph(AgentState)
        self.search_manager = SearchManager(
            backend=config.search_backend,
            api_key=config.tavily_api_key
        )
        self.search_tools = SearchToolInterface(self.search_manager)
        self._build_graph()

    def _build_graph(self):
        """LangGraph 워크플로우 구성"""

        # 노드 추가
        self.graph_builder.add_node("clarify_request", self._clarify_request)
        self.graph_builder.add_node("supervisor", self._supervisor_node)
        self.graph_builder.add_node("parallel_researchers", self._parallel_researchers)
        self.graph_builder.add_node("compress_results", self._compress_results)
        self.graph_builder.add_node("generate_report", self._generate_report)

        # 엣지 설정
        self.graph_builder.add_edge(START, "clarify_request")
        self.graph_builder.add_edge("clarify_request", "supervisor")
        self.graph_builder.add_conditional_edges(
            "supervisor",
            self._should_continue_research,
            {
                "continue": "parallel_researchers",
                "finalize": "compress_results"
            }
        )
        self.graph_builder.add_edge("parallel_researchers", "supervisor")
        self.graph_builder.add_edge("compress_results", "generate_report")
        self.graph_builder.add_edge("generate_report", END)

        self.graph = self.graph_builder.compile()

    async def _clarify_request(self, state: AgentState) -> AgentState:
        """
        Step 1: 사용자 입력 명확화
        입력: search_topic
        출력: research_brief
        """
        prompt = PROMPTS["clarify"].format(search_topic=state["search_topic"])

        # Anthropic API 호출 (실제 구현)
        response = self._call_llm(prompt, config.supervisor_model)

        try:
            import json
            research_brief = json.loads(response)
        except:
            research_brief = {"main_topic": state["search_topic"], "research_questions": []}

        state["research_brief"] = str(research_brief)
        state["messages"].append(AIMessage(content=f"Research brief: {research_brief}"))

        return state

    async def _supervisor_node(self, state: AgentState) -> AgentState:
        """
        Step 2: 감독자 에이전트
        역할: 연구 계획 수립 및 결과 평가
        """
        prompt = PROMPTS["supervisor"].format(
            research_brief=state["research_brief"],
            notes="\n".join(state["notes"][:3])  # 최근 3개 노트만
        )

        response = self._call_llm(prompt, config.supervisor_model)
        state["messages"].append(AIMessage(content=response))

        return state

    async def _parallel_researchers(self, state: AgentState) -> AgentState:
        """
        Step 3: 병렬 연구원 실행
        여러 연구 질문을 동시에 처리
        """
        import asyncio

        # 감독자의 작업 지시 파싱 (실제 구현에서는 JSON 파싱)
        research_queries = [
            "Find latest AI research trends",
            "Compare major LLM models",
            "Understand agent-based systems"
        ]

        # 병렬 실행
        tasks = [
            self._researcher_agent(query)
            for query in research_queries[:config.max_concurrent_researchers]
        ]

        results = await asyncio.gather(*tasks)

        # 결과 수집
        for result in results:
            if result:
                state["raw_notes"].extend(result)
                state["notes"].append(result[0] if result else "")

        state["current_iteration"] += 1
        return state

    async def _researcher_agent(self, query: str) -> list[dict]:
        """
        개별 연구원 에이전트
        검색 및 분석 수행
        """
        results = []

        # Step 1: 검색 실행
        search_result = await self.search_tools.search(query, num_results=5)

        for result in search_result["results"]:
            results.append({
                "query": query,
                "url": result["url"],
                "title": result["title"],
                "content": result["content"],
                "score": result["score"]
            })

        return results

    def _should_continue_research(self, state: AgentState) -> str:
        """
        조건부 라우팅: 추가 연구 필요 여부 판단
        """
        if state["current_iteration"] >= config.max_supervisor_iterations:
            return "finalize"

        # 실제 구현: 감독자의 판단에 따라 결정
        return "continue" if state["current_iteration"] < 2 else "finalize"

    async def _compress_results(self, state: AgentState) -> AgentState:
        """
        Step 4: 결과 압축
        중복 제거 및 정보 정리
        """
        prompt = PROMPTS["compress"].format(
            raw_notes="\n".join(str(n) for n in state["raw_notes"])
        )

        response = self._call_llm(prompt, config.compression_model)
        state["messages"].append(AIMessage(content=f"Compressed: {response}"))

        return state

    async def _generate_report(self, state: AgentState) -> AgentState:
        """
        Step 5: 최종 보고서 생성
        마크다운 형식의 전문적 보고서
        """
        prompt = PROMPTS["final_report"].format(
            search_topic=state["search_topic"],
            notes="\n".join(state["notes"])
        )

        response = self._call_llm(prompt, config.supervisor_model)
        state["final_report"] = response
        state["messages"].append(AIMessage(content=response))

        return state

    def _call_llm(self, prompt: str, model: str) -> str:
        """LLM API 호출 (placeholder - 실제 구현 필요)"""
        # 실제 구현: Anthropic API 호출
        return f"[LLM Response from {model}]"

    async def ainvoke(self, input_data: dict) -> dict:
        """비동기 워크플로우 실행"""
        initial_state: AgentState = {
            "messages": [HumanMessage(content=input_data["search_topic"])],
            "search_topic": input_data["search_topic"],
            "research_brief": "",
            "raw_notes": [],
            "notes": [],
            "final_report": "",
            "current_iteration": 0,
            "need_more_research": False,
        }

        result = await self.graph.ainvoke(initial_state)
        return result
