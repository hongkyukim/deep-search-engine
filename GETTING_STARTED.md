# 🚀 빠른 시작 가이드

LangChain Deep Research 패턴을 구현한 **에이전트 기반 검색 시스템**을 시작하는 가이드입니다.

---

## 📦 설치 (5분)

### 1단계: 의존성 설치
```bash
cd /Users/hongkyukim/wkREA
pip install -r requirements.txt
```

**설치되는 패키지:**
- `langgraph`: 워크플로우 관리 (선택적)
- `langchain`: LLM 체인
- `anthropic`: Claude API 클라이언트
- `aiohttp`: 비동기 HTTP 요청
- `tenacity`: 재시도 로직
- `python-dotenv`: 환경변수 관리

### 2단계: API 키 설정
```bash
# 1. .env 파일 생성
cp .env.example .env

# 2. .env 파일 편집
# ANTHROPIC_API_KEY=sk-ant-... (필수)
# TAVILY_API_KEY=tvly-...       (권장)
```

**API 키 얻기:**
- **Anthropic**: https://console.anthropic.com → API Keys
- **Tavily**: https://tavily.com → Dashboard

---

## 💡 기본 사용법 (10분)

### 최소 코드로 시작

```python
# quick_start.py
import asyncio
from main import DeepSearchEngine

async def main():
    # 엔진 초기화
    engine = DeepSearchEngine()
    
    # 검색 실행
    result = await engine.search(
        topic="당신의 검색 주제",
        verbose=True
    )
    
    # 최종 보고서 출력
    print("\n📄 최종 보고서:\n")
    print(result["report"])

# 실행
asyncio.run(main())
```

**실행:**
```bash
python quick_start.py
```

---

## 📊 결과 구조

```python
result = {
    "topic": "검색 주제",
    "research_brief": {
        "main_topic": "주제",
        "research_questions": ["질문1", "질문2"],
        "scope": "broad/focused/specific",
        "expected_depth": "basic/intermediate/expert"
    },
    "notes": [
        {"query": "검색어", "summary": "요약"},
        ...
    ],
    "compressed": {
        "key_findings": ["발견1", "발견2"],
        "sources": [{"title": "...", "relevance": "high"}],
        "gaps": "추가 정보 필요",
        "confidence_score": 0.85
    },
    "report": "# 최종 보고서\n...",
    "search_history": [...],
    "iterations": 3
}
```

---

## 🎯 실제 사용 예제

### 예제 1: 기술 트렌드 조사
```python
result = await engine.search(
    topic="2024년 AI 에이전트 기술의 최신 동향",
    verbose=True
)

# 결과 활용
print(f"✅ 반복: {result['iterations']}")
print(f"📊 발견: {len(result['compressed']['key_findings'])} 개")
print(f"📈 신뢰도: {result['compressed']['confidence_score']:.1%}")
```

### 예제 2: 경쟁사 분석
```python
competitors = ["ChatGPT", "Claude", "Gemini"]

for competitor in competitors:
    result = await engine.search(f"{competitor}의 주요 특징")
    print(f"\n{competitor}:")
    for finding in result['compressed']['key_findings'][:3]:
        print(f"  • {finding}")
```

### 예제 3: 결과 저장
```python
import json

result = await engine.search("주제")

# JSON으로 저장
with open("research_result.json", "w", encoding="utf-8") as f:
    json.dump({
        "topic": result["topic"],
        "key_findings": result["compressed"]["key_findings"],
        "report": result["report"]
    }, f, ensure_ascii=False, indent=2)
```

---

## ⚙️ 설정 커스터마이징

### 빠른 검색 (비용 절감)
```python
from config import config

config.max_supervisor_iterations = 2      # 반복 줄이기
config.max_concurrent_researchers = 2     # 동시 연구원 줄이기
config.supervisor_model = "claude-3-5-haiku-20241022"  # 더 저렴한 모델

engine = DeepSearchEngine()
result = await engine.search("주제")
```

### 깊이 있는 검색 (품질 향상)
```python
from config import config

config.max_supervisor_iterations = 5      # 반복 늘리기
config.max_concurrent_researchers = 5     # 동시 연구원 늘리기
config.supervisor_model = "claude-3-opus-20250219"  # 더 강력한 모델

engine = DeepSearchEngine()
result = await engine.search("주제")
```

---

## 🔍 워크플로우 이해하기

### 단계별 동작

```
1️⃣ 입력 명확화 (Clarification)
   • 사용자 입력 분석
   • 리서치 브리프 생성
   • 연구 질문 도출

2️⃣ 감독자 계획 (Supervisor Planning)
   • 연구 작업 분해
   • 3-5개 세부 질문 생성
   • 우선순위 설정

3️⃣ 병렬 연구 (Parallel Research) [동시 실행]
   • 웹 검색 (Tavily/Google/DuckDuckGo)
   • 결과 분석
   • 추가 검색 판단

4️⃣ 감독자 평가 (Supervisor Evaluation)
   • 정보 충분성 검토
   • 신뢰도 계산
   • 계속? 종료? 결정

   반복 3-4 (최대 N회)

5️⃣ 정보 압축 (Compression)
   • 중복 제거
   • 무관한 정보 필터링
   • 원본 보존

6️⃣ 최종 보고서 (Report Generation)
   • Executive Summary
   • Key Findings
   • Detailed Analysis
   • Sources & Limitations
```

---

## 📈 성능 모니터링

```python
import time

start = time.time()

result = await engine.search("주제", verbose=True)

elapsed = time.time() - start

print(f"\n⏱️  실행 시간: {elapsed:.1f}초")
print(f"🔄 반복 횟수: {result['iterations']}")
print(f"🔎 검색 요청: {len(result['search_history'])}")
print(f"💡 핵심 발견: {len(result['compressed']['key_findings'])}")
print(f"📈 신뢰도: {result['compressed']['confidence_score']:.1%}")
```

---

## 🛠️ 문제 해결

### 문제 1: "API Key Error"
```
❌ Error: No API key found

해결:
1. .env 파일에 ANTHROPIC_API_KEY 추가
2. 환경변수 재로드: export $(cat .env | xargs)
```

### 문제 2: "TimeoutError"
```
❌ Error: Search timeout

해결:
1. 네트워크 연결 확인
2. search_backend 변경: config.search_backend = "duckduckgo"
3. 타임아웃 증가: timeout=20
```

### 문제 3: "Too many requests"
```
❌ Error: Rate limit exceeded

해결:
1. max_concurrent_researchers 줄이기 (3 → 2)
2. max_supervisor_iterations 줄이기 (5 → 2)
3. 검색 간격 추가
```

### 문제 4: "Token limit exceeded"
```
❌ Error: Max tokens exceeded

해결:
1. 더 저렴한 모델 사용: claude-3-5-haiku
2. max_tokens 감소
3. 반복 횟수 줄이기
```

---

## 📚 다음 단계

### 1단계 완료: 기본 검색 작동 확인
```bash
python -c "
import asyncio
from main import DeepSearchEngine

async def test():
    engine = DeepSearchEngine()
    result = await engine.search('테스트')
    print('✅ 기본 검색 작동 중')

asyncio.run(test())
"
```

### 2단계: 예제 실행
```bash
python examples.py
```

### 3단계: 커스텀 프로젝트 시작
```python
# my_research.py
import asyncio
from main import DeepSearchEngine
from config import config

async def research_trend():
    # 설정 커스터마이징
    config.max_supervisor_iterations = 3
    
    # 엔진 생성
    engine = DeepSearchEngine()
    
    # 검색 실행
    result = await engine.search(
        topic="당신의 연구 주제",
        verbose=True
    )
    
    # 결과 활용
    print(result["report"])

asyncio.run(research_trend())
```

---

## 🎓 핵심 개념 이해

### 1. 감독자-연구원 패턴
- **감독자**: 전체 연구 계획 및 평가
- **연구원**: 개별 검색 및 분석 (병렬 실행)
- **장점**: 효율성 ↑, 비용 최적화, 신뢰도 향상

### 2. 병렬 처리
- 여러 연구 질문을 **동시에** 처리
- 검색 속도 향상
- 다각도 분석 가능

### 3. 반복적 탐색
- 감독자가 추가 연구 필요 판단
- 필요시에만 재검색
- 불필요한 비용 절감

### 4. 정보 보존
- 요약이 아닌 **원본 보존**
- 정보 손실 최소화
- 신뢰도 향상

---

## 💰 비용 추정

| 항목 | 비용 |
|------|------|
| Claude 3.5 Sonnet (10K tokens) | ~$0.30 |
| Tavily 검색 (5회) | ~$0.05 |
| **평균 검색당 총 비용** | **~$0.35-$1.00** |

**절감 팁:**
- Haiku 모델 사용 (Sonnet의 1/10 가격)
- 반복 횟수 제한
- DuckDuckGo 사용 (무료)

---

## 📞 지원

- **버그 리포트**: GitHub Issues
- **기능 요청**: GitHub Discussions
- **문서**: README.md, examples.py 참고

---

## ✅ 체크리스트

- [ ] 의존성 설치 (`pip install -r requirements.txt`)
- [ ] API 키 설정 (.env 파일)
- [ ] 기본 검색 테스트 (quick_start.py)
- [ ] 예제 실행 (examples.py)
- [ ] 커스텀 설정 시도
- [ ] 프로젝트 시작 ✨

---

**축하합니다! 이제 준비가 완료되었습니다.** 🎉

더 자세한 정보는 [README.md](README.md)를 참고하세요.
