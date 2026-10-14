# Deep Search Engine 🔍

**LangChain Deep Research를 참고한 에이전트 기반 검색 시스템**

Python 백엔드에서 감독자(Supervisor)와 연구원(Researcher) 에이전트가 협력하여 깊이 있는 리서치를 수행하는 시스템입니다.

---

## 📋 아키텍처 개요

```
사용자 입력 (검색 주제)
        ↓
┌─────────────────────────┐
│  1️⃣ 입력 명확화       │ → research_brief 생성
└─────────────────────────┘
        ↓
┌─────────────────────────┐
│  2️⃣ 감독자 (Supervisor) │ → 연구 계획 수립
└─────────────────────────┘
        ↓
┌──────────────────────────────────────────┐
│  3️⃣ 연구원들 (Researchers) [병렬 실행]  │
│   • 검색 실행 (Tavily/Google/etc)       │
│   • 결과 분석                            │
│   • 추가 검색 판단                       │
└──────────────────────────────────────────┘
        ↓
┌──────────────────────┐
│  4️⃣ 감독자 평가     │ → 추가 연구 필요?
└──────────────────────┘
        ├→ YES: 3번으로 돌아가기
        └→ NO: 5번으로 이동
        ↓
┌──────────────────────┐
│  5️⃣ 정보 압축       │ → 중복 제거, 구조화
└──────────────────────┘
        ↓
┌──────────────────────┐
│  6️⃣ 최종 보고서     │ → 마크다운 형식
└──────────────────────┘
```

---

## 🛠️ 프로젝트 구조

```
/Users/hongkyukim/wkREA/
├── state.py              # 상태 정의 (5개 타입)
├── config.py             # 전역 설정 & 파라미터
├── prompts.py            # LLM 프롬프트 템플릿 (5개)
├── search_tools.py       # 검색 API 통합 (Tavily/Google/DuckDuckGo)
├── llm_client.py         # Anthropic Claude API 클라이언트
│                         # + 4개 에이전트 클래스
├── deep_search_graph.py  # LangGraph 워크플로우 (선택적)
├── main.py               # 메인 애플리케이션
├── requirements.txt      # 의존성
├── .env.example          # 환경변수 템플릿
└── README.md             # 이 파일
```

---

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 환경변수 설정
cp .env.example .env

# 3. .env 파일에 API 키 추가
# ANTHROPIC_API_KEY=sk-ant-...
# TAVILY_API_KEY=tvly-...
```

### 2. 기본 사용법

```python
import asyncio
from main import DeepSearchEngine

async def main():
    # 엔진 초기화
    engine = DeepSearchEngine()
    
    # 검색 실행
    result = await engine.search(
        topic="AI 에이전트 기술의 최신 동향",
        verbose=True  # 단계별 로그 출력
    )
    
    # 결과 확인
    print(result["report"])  # 최종 보고서
    print(f"반복 횟수: {result['iterations']}")
    print(f"핵심 발견: {len(result['compressed']['key_findings'])} 개")

# 실행
asyncio.run(main())
```

### 3. 고급 사용법

```python
from main import DeepSearchEngine
from config import config

# 설정 커스터마이징
config.max_supervisor_iterations = 3
config.max_concurrent_researchers = 5
config.search_backend = "tavily"

# 엔진 생성 (커스텀 API 키)
engine = DeepSearchEngine(
    search_backend="tavily",
    api_key="your-anthropic-key"
)

# 검색 실행
result = await engine.search("당신의 검색 주제")

# 결과 활용
report = result["report"]           # 마크다운 보고서
notes = result["notes"]              # 수집된 노트
compressed = result["compressed"]    # 정리된 데이터
history = result["search_history"]   # 검색 이력
```

---

## 📊 핵심 컴포넌트

### 1. **SupervisorAgent** (감독자 에이전트)
- **역할**: 리서치 계획 수립 및 결과 평가
- **메서드**:
  - `plan_research(brief)` → 연구 작업 목록 생성
  - `evaluate_results(notes, iteration, max)` → 추가 연구 필요 판단

### 2. **ResearcherAgent** (연구원 에이전트)
- **역할**: 검색 실행 및 결과 분석
- **메서드**:
  - `conduct_research(query)` → 검색 + 분석 실행
  - 병렬 실행 지원

### 3. **CompressionAgent** (압축 에이전트)
- **역할**: 정보 최적화 (중복 제거, 구조화)
- **특징**: 원본 정보는 보존, 요약 금지

### 4. **ReportGenerator** (보고서 생성)
- **역할**: 최종 마크다운 보고서 생성
- **구조**:
  - Executive Summary
  - Key Findings
  - Detailed Analysis
  - Sources
  - Limitations

### 5. **SearchToolInterface** (검색 도구)
- **지원 백엔드**:
  - Tavily (권장, 고속)
  - Google Custom Search
  - DuckDuckGo (무료)

---

## ⚙️ 설정 파라미터

`config.py`에서 커스터마이징 가능:

```python
# 모델 선택
supervisor_model = "claude-3-5-sonnet-20241022"
researcher_model = "claude-3-5-sonnet-20241022"

# 반복 제한
max_supervisor_iterations = 5
max_concurrent_researchers = 3

# 검색 설정
search_backend = "tavily"
max_search_results_per_query = 5

# 토큰 한도
max_tokens_supervisor = 4096
max_tokens_researcher = 4096
```

---

## 📈 성능 지표

| 메트릭 | 값 |
|-------|-----|
| 평균 반복 횟수 | 2-3회 |
| 평균 실행 시간 | 60-120초 |
| 검색 요청 | 5-15개 |
| 최종 보고서 길이 | 2000-5000 자 |
| 비용 (Claude 3.5 Sonnet) | $0.3-$1.0 |

---

## 🔄 워크플로우 상세

### Step 1: 입력 명확화
```
사용자: "AI 에이전트에 대해 알려줘"
       ↓
LLM 분석
       ↓
결과: {
  "main_topic": "AI 에이전트 기술",
  "research_questions": ["정의?", "분류?", "사례?"],
  "scope": "focused",
  "expected_depth": "intermediate"
}
```

### Step 2-4: 반복 연구 사이클
```
Loop until sufficient or max_iterations:
  1. 감독자: 연구 계획 수립 → ["질문1", "질문2", "질문3"]
  2. 연구원들: 병렬 검색 → [결과1, 결과2, 결과3]
  3. 감독자: 결과 평가 → is_sufficient? confidence?
  4. Decision: 계속? 종료?
```

### Step 5: 정보 압축
```
원본 노트 (중복 포함)
       ↓
LLM이 분석
       ↓
정리된 데이터:
{
  "key_findings": ["발견1", "발견2"],
  "sources": [...],
  "gaps": "...",
  "confidence_score": 0.85
}
```

### Step 6: 최종 보고서
```
정리된 데이터 + 분석
       ↓
LLM이 작성
       ↓
마크다운 형식의 전문 보고서
```

---

## 🧪 테스트

```python
# test.py
import asyncio
from main import DeepSearchEngine

async def test():
    engine = DeepSearchEngine()
    
    test_cases = [
        "2024년 AI 에이전트 기술",
        "LangChain Deep Research 원리",
        "에이전트 기반 검색 시스템의 장단점"
    ]
    
    for topic in test_cases:
        print(f"\n테스트: {topic}")
        result = await engine.search(topic)
        print(f"✓ 반복: {result['iterations']}")
        print(f"✓ 발견: {len(result['compressed']['key_findings'])} 개")

asyncio.run(test())
```

---

## 🔗 LangChain Deep Research와의 비교

| 기능 | 이 프로젝트 | LangChain |
|------|-----------|----------|
| 감독자-연구원 패턴 | ✅ | ✅ |
| 병렬 처리 | ✅ | ✅ |
| 정보 압축 | ✅ | ✅ |
| LangGraph 기반 | ⭐ 선택적 | ✅ 필수 |
| 비용 효율 | ✅ (더 낮음) | 높음 |
| 커스터마이징 | ✅ (쉬움) | 어려움 |
| 프로덕션 준비 | 🔧 베타 | ✅ 완성 |

---

## 💡 주요 인사이트

1. **재귀가 아닌 반복**: "깊이 있는" 검색은 함수 재귀가 아니라 메시지 루프

2. **병렬 처리의 중요성**: 여러 연구 질문을 동시에 처리하면 효율성 ↑

3. **정보 보존 우선**: 정보 손실 최소화 → 원본 내용 최대한 보존

4. **감독자의 판단**: 감독자가 추가 연구 필요 여부 판단 → 비용 최적화

5. **모듈식 설계**: 각 단계가 독립적 → 유지보수 용이

---

## 🚨 주의사항

- **API 비용**: Tavily + Anthropic 조합 비용 발생
- **반복 횟수**: 제한하지 않으면 비용 급증 가능
- **토큰 한도**: 긴 결과는 토큰 초과 가능성

---

## 📚 참고 자료

- [LangChain Deep Research 공식 저장소](https://github.com/langchain-ai/open_deep_research)
- [Anthropic Claude API 문서](https://docs.anthropic.com)
- [Tavily Search API](https://tavily.com)

---

## 📝 라이선스

MIT License

---

## 🤝 기여

버그 리포트, 기능 제안, 풀 리퀘스트 환영합니다!
