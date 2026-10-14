# 🏗️ 아키텍처 상세 설명

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    Deep Search Engine                        │
│                   (main.py - 진입점)                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────┼─────────────────────┐
        ↓                     ↓                     ↓
   ┌─────────┐         ┌───────────┐         ┌──────────┐
   │  State  │         │  LLM      │         │ Search   │
   │ (state) │         │ (llm_     │         │ Tools    │
   │         │         │  client)  │         │ (search_ │
   │ TypedDict           │         │         │  tools)  │
   │ 타입 정의            │ Claude  │         │          │
   │         │         │ API 호출  │         │ Tavily   │
   └─────────┘         └───────────┘         │ Google   │
                            ↑                 │ Duck..   │
                            │                 └──────────┘
        ┌───────────────────┼──────────────────┐
        ↓                   ↓                  ↓
   ┌──────────┐      ┌─────────────┐    ┌──────────┐
   │ Supervisor       │ Researcher  │    │ Compression
   │ Agent    │      │ Agent       │    │ Agent
   │          │      │             │    │
   │ • 계획   │      │ • 검색      │    │ • 정보 정리
   │ • 평가   │      │ • 분석      │    │ • 중복 제거
   │ • 반복   │      │ • 반복 판단 │    │ • 구조화
   └──────────┘      └─────────────┘    └──────────┘
        ↑                   ↑                  ↑
        └───────────────────┼──────────────────┘
                            ↓
                   ┌──────────────────┐
                   │ Report Generator │
                   │                  │
                   │ • 마크다운 형식  │
                   │ • 최종 보고서    │
                   └──────────────────┘
                            ↓
                   ┌──────────────────┐
                   │  최종 결과       │
                   │  (report.md)     │
                   └──────────────────┘
```

---

## 모듈 역할

### 1. `state.py` - 상태 정의
**목적**: TypedDict로 모든 상태를 명확히 정의

```python
AgentState          # 전체 워크플로우 상태
├─ messages         # LLM 메시지 (자동 병합)
├─ search_topic     # 입력 주제
├─ research_brief   # 명확화된 브리프
├─ raw_notes        # 원본 노트
├─ notes            # 정리된 노트
├─ final_report     # 최종 보고서
├─ current_iteration # 반복 카운트
└─ need_more_research # 추가 연구 필요

SupervisorState     # 감독자 상태
├─ research_plan
└─ pending_tasks

ResearcherState     # 연구원 상태
├─ research_query
├─ search_results
└─ summary
```

**장점**: 타입 안전성, 자동 완성, 버그 감소

---

### 2. `config.py` - 설정 관리
**목적**: 모든 파라미터를 한곳에서 관리

```python
SearchConfig
├─ 모델 선택
│  ├─ supervisor_model
│  ├─ researcher_model
│  └─ compression_model
├─ 토큰 한도
│  ├─ max_tokens_supervisor
│  ├─ max_tokens_researcher
│  └─ max_tokens_compression
├─ 반복 제한
│  ├─ max_supervisor_iterations
│  ├─ max_researcher_iterations
│  └─ max_concurrent_researchers
├─ 검색 설정
│  ├─ search_backend
│  ├─ max_search_results_per_query
│  └─ enable_web_scraping
└─ API 키
   ├─ anthropic_api_key
   └─ tavily_api_key
```

**사용**: `from config import config` → `config.max_supervisor_iterations = 3`

---

### 3. `prompts.py` - LLM 프롬프트
**목적**: 각 단계별 프롬프트 템플릿 저장

```
CLARIFY_PROMPT       # Step 1: 입력 명확화
   ↓ 명확화된 research_brief 생성

SUPERVISOR_PROMPT    # Step 2: 계획 수립
   ↓ 연구 작업 목록 생성

RESEARCHER_PROMPT    # Step 3: 검색 및 분석
   ↓ 검색 결과 + 분석

COMPRESS_PROMPT      # Step 5: 정보 압축
   ↓ 정리된 데이터

FINAL_REPORT_PROMPT  # Step 6: 보고서 생성
   ↓ 최종 마크다운 보고서
```

**구조**:
- 역할 명시
- 입력 데이터 제공
- 출력 형식 지정
- JSON/마크다운 강제

---

### 4. `search_tools.py` - 검색 도구
**목적**: 다양한 검색 API 통합

```
SearchManager
├─ _tavily_search()      # Tavily API
├─ _google_search()      # Google Custom Search
└─ _duckduckgo_search()  # DuckDuckGo

SearchToolInterface
├─ search(query)         # 검색 실행
├─ think(reflection)     # 사고 도구
└─ get_search_history()  # 검색 이력 조회
```

**특징**:
- 비동기 처리 (asyncio)
- 재시도 로직 (tenacity)
- 결과 표준화
- 타임아웃 처리

---

### 5. `llm_client.py` - LLM 클라이언트
**목적**: Anthropic Claude API 통합

```
LLMClient               # 기본 LLM 호출
├─ call()              # 일반 호출
└─ call_json()         # JSON 응답

SupervisorAgent        # 감독자 에이전트
├─ plan_research()     # 계획 수립
└─ evaluate_results()  # 평가

ResearcherAgent        # 연구원 에이전트
└─ conduct_research()  # 검색 + 분석

CompressionAgent       # 압축 에이전트
└─ compress()          # 정보 압축

ReportGenerator        # 보고서 생성
└─ generate()          # 최종 보고서 생성
```

**특징**:
- 메시지 히스토리 추적
- 에러 처리
- JSON 파싱
- 대화 이력 관리

---

### 6. `main.py` - 메인 애플리케이션
**목적**: 모든 컴포넌트 통합

```
DeepSearchEngine
├─ search()  # 메인 검색 메서드
│  ├─ Step 1: _clarify_request()
│  ├─ Loop:
│  │  ├─ Step 2: _plan_research()
│  │  ├─ Step 3: _conduct_research()
│  │  └─ Step 4: _evaluate_results()
│  ├─ Step 5: _compress_results()
│  └─ Step 6: _generate_report()
└─ 결과 반환
```

**워크플로우**:
```
사용자 입력
   ↓
명확화 (step 1)
   ↓
반복 루프 (steps 2-4)
   └─ 감독자 계획 → 병렬 연구 → 평가
   └─ 추가 필요? → 반복 또는 종료
   ↓
압축 (step 5)
   ↓
보고서 생성 (step 6)
   ↓
결과 반환
```

---

## 데이터 흐름

### 입력 → 처리 → 출력

```
Input:
{
  "search_topic": "AI 에이전트"
}
        ↓
Processing:
Step 1: 명확화
  research_brief = {
    "main_topic": "AI 에이전트",
    "research_questions": [...],
    "scope": "focused",
    "expected_depth": "intermediate"
  }

Step 2-4: 반복 연구
  raw_notes = [
    {"query": "...", "results": [...]},
    {"query": "...", "results": [...]},
    ...
  ]

Step 5: 압축
  compressed = {
    "key_findings": [...],
    "sources": [...],
    "gaps": "...",
    "confidence_score": 0.85
  }

Step 6: 보고서
  report = "# AI 에이전트\n..."
        ↓
Output:
{
  "topic": "AI 에이전트",
  "research_brief": {...},
  "notes": [...],
  "compressed": {...},
  "report": "...",
  "search_history": [...],
  "iterations": 3
}
```

---

## 에이전트 상호작용

### 감독자 vs 연구원

```
감독자 (Supervisor)
├─ 역할: 지휘관, 평가자
├─ 책임:
│  ├─ 연구 계획 수립
│  ├─ 세부 질문 생성
│  ├─ 결과 평가
│  └─ 추가 연구 판단
├─ 실행 빈도: 반복마다 1회
└─ 특징: 전략적 사고

연구원 (Researcher)
├─ 역할: 현장 조사원
├─ 책임:
│  ├─ 웹 검색 실행
│  ├─ 결과 분석
│  └─ 추가 검색 판단
├─ 실행 빈도: 병렬로 여러 개
└─ 특징: 전술적 실행
```

### 상호작용 플로우

```
감독자: "다음 질문들을 조사해줘"
   ↓
연구원들 (병렬):
  • 질문1 → 검색 → 분석 → 결과
  • 질문2 → 검색 → 분석 → 결과
  • 질문3 → 검색 → 분석 → 결과
   ↓
감독자: "결과를 평가해보니... 추가 조사 필요"
   ↓
연구원들 (재실행):
  • 질문4 → 검색 → 분석 → 결과
   ↓
감독자: "이제 충분합니다"
   ↓
압축 및 보고서 생성
```

---

## 병렬 처리 메커니즘

```python
# Step 3: 병렬 연구 실행
research_tasks = [
    researcher.conduct_research("질문1"),
    researcher.conduct_research("질문2"),
    researcher.conduct_research("질문3"),
]

# asyncio.gather로 동시 실행
results = await asyncio.gather(*research_tasks)

# 결과: [결과1, 결과2, 결과3] (순차 실행보다 3배 빠름)
```

**이점**:
- 속도 향상 (병렬도 = 3배)
- 다각도 분석
- 비용 효율성 (쿼리 수 감소 가능)

---

## 확장성

### 1. 새로운 검색 백엔드 추가

```python
# search_tools.py에 추가
async def _bing_search(self, query: str, max_results: int) -> list[dict]:
    # Bing API 호출
    return formatted_results

# config.py 수정
search_backend: Literal["tavily", "google", "duckduckgo", "bing"] = "bing"
```

### 2. 새로운 에이전트 추가

```python
# llm_client.py에 추가
class ValidationAgent:
    """검색 결과 검증"""
    def validate(self, results: list) -> dict:
        # 검증 로직
        return validation_result

# main.py에 통합
self.validator = ValidationAgent(self.llm)
```

### 3. 커스텀 프롬프트

```python
# prompts.py에 추가
CUSTOM_PROMPT = """당신의 커스텀 프롬프트"""

# main.py에서 사용
response = self.llm.call(
    prompt=PROMPTS["custom"],
    model=config.supervisor_model
)
```

---

## 성능 최적화

### 1. 토큰 사용량 감소
- Haiku 모델 사용 (더 저렴)
- max_tokens 제한
- 불필요한 메시지 삭제

### 2. 실행 시간 감소
- max_supervisor_iterations 줄이기
- 병렬 처리 극대화
- 비동기 I/O 활용

### 3. 신뢰도 향상
- 반복 횟수 늘리기
- 더 강력한 모델 사용
- 검색 결과 수 증가

---

## 에러 처리

```
검색 실패 → 재시도 로직 (tenacity)
   ↓
여전히 실패 → 에러 메시지 반환
   ↓
LLM 호출 실패 → 재시도 또는 대체 모델
   ↓
타임아웃 → 부분 결과 반환
   ↓
토큰 초과 → 히스토리 삭제 후 재시도
```

---

**이 아키텍처는 확장 가능하고 유지보수하기 쉽게 설계되었습니다.** ✨
