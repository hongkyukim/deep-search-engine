"""
검색 도구 통합 (Tavily, Google, DuckDuckGo)
"""

import asyncio
import json
from typing import Optional
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential


class SearchManager:
    """검색 백엔드 관리자"""

    def __init__(self, backend: str = "tavily", api_key: Optional[str] = None):
        self.backend = backend
        self.api_key = api_key

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def search(self, query: str, max_results: int = 5) -> list[dict]:
        """검색 실행 (재시도 로직 포함)"""

        if self.backend == "tavily":
            return await self._tavily_search(query, max_results)
        elif self.backend == "google":
            return await self._google_search(query, max_results)
        else:
            return await self._duckduckgo_search(query, max_results)

    async def _tavily_search(self, query: str, max_results: int) -> list[dict]:
        """Tavily API를 사용한 검색"""
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": max_results,
            "include_answer": True,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return self._format_results(data.get("results", []), "tavily")
                else:
                    raise Exception(f"Tavily API error: {resp.status}")

    async def _google_search(self, query: str, max_results: int) -> list[dict]:
        """Google Custom Search 구현 (placeholder)"""
        # 실제 구현: Google Custom Search API 사용
        return []

    async def _duckduckgo_search(self, query: str, max_results: int) -> list[dict]:
        """DuckDuckGo 검색 구현 (placeholder)"""
        # 실제 구현: duckduckgo-search 라이브러리 사용
        return []

    def _format_results(self, results: list, source: str) -> list[dict]:
        """검색 결과를 표준 형식으로 변환"""
        formatted = []
        for result in results:
            formatted.append({
                "url": result.get("url", ""),
                "title": result.get("title", ""),
                "content": result.get("content", result.get("snippet", "")),
                "source": source,
                "score": result.get("score", 0.5),
            })
        return formatted


async def scrape_webpage(url: str, timeout: int = 10) -> str:
    """웹페이지 내용 스크래핑"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout) as resp:
                if resp.status == 200:
                    return await resp.text()
    except asyncio.TimeoutError:
        return f"[Timeout scraping {url}]"
    except Exception as e:
        return f"[Error scraping {url}: {str(e)}]"


class SearchToolInterface:
    """LLM이 호출할 검색 도구 인터페이스"""

    def __init__(self, search_manager: SearchManager):
        self.search_manager = search_manager
        self.search_history = []

    async def search(self, query: str, num_results: int = 5) -> dict:
        """검색 도구 (LLM이 호출)"""
        results = await self.search_manager.search(query, num_results)
        self.search_history.append({
            "query": query,
            "results_count": len(results),
            "results": results
        })
        return {
            "status": "success",
            "query": query,
            "results": results,
            "total": len(results)
        }

    async def think(self, reflection: str) -> dict:
        """생각 도구 (추가 분석 필요 여부 판단)"""
        return {
            "status": "recorded",
            "reflection": reflection,
            "next_step": "continue_search" if len(reflection) > 50 else "finalize"
        }

    def get_search_history(self) -> list:
        """검색 이력 조회"""
        return self.search_history
