"""
에이전트 기반 검색 시스템 설정
"""

from dataclasses import dataclass
from typing import Literal
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class SearchConfig:
    """검색 설정"""
    # 모델 설정
    supervisor_model: str = "claude-opus-4-1-20250805"  # 감독자
    researcher_model: str = "claude-opus-4-1-20250805"   # 연구원
    compression_model: str = "claude-opus-4-1-20250805"  # 압축

    # 토큰 한도
    max_tokens_supervisor: int = 4096
    max_tokens_researcher: int = 4096
    max_tokens_compression: int = 2048

    # 반복 제한
    max_supervisor_iterations: int = 5  # 감독자 최대 반복
    max_researcher_iterations: int = 3  # 연구원당 최대 반복
    max_concurrent_researchers: int = 3  # 동시 연구원 수

    # 검색 설정
    search_backend: Literal["tavily", "google", "duckduckgo"] = "tavily"
    max_search_results_per_query: int = 5
    enable_web_scraping: bool = True

    # API 키
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")

    # 출력 형식
    output_format: Literal["markdown", "html", "json"] = "markdown"
    compress_results: bool = True  # 결과 압축 활성화
    preserve_sources: bool = True  # 원본 출처 보존


# 기본 설정 인스턴스
config = SearchConfig()
