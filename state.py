"""
에이전트 기반 검색 시스템의 상태 정의
LangChain Deep Research 패턴을 따름
"""

from typing import Annotated, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """전체 워크플로우의 상태 관리"""
    messages: Annotated[list, add_messages]  # 메시지 누적 (자동 병합)
    search_topic: str                         # 사용자 입력 검색어
    research_brief: str                       # 명확화된 리서치 주제
    raw_notes: Annotated[list, lambda x, y: y] = []  # 원문 노트 (override)
    notes: list = []                          # 정리된 노트
    final_report: str = ""                    # 최종 보고서
    current_iteration: int = 0                # 반복 카운트
    need_more_research: bool = False          # 추가 연구 필요 여부


class SupervisorState(TypedDict):
    """감독자 에이전트의 상태"""
    messages: Annotated[list, add_messages]
    research_plan: dict  # {task_id: {"query": str, "status": "pending|done"}}
    pending_tasks: list[str]
    completed_tasks: list[str]


class ResearcherState(TypedDict):
    """연구원 에이전트의 상태"""
    messages: Annotated[list, add_messages]
    research_query: str
    search_results: list[dict]  # {url, title, content, score}
    summary: str
    iteration_count: int = 0
