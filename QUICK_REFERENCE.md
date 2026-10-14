# ⚡ 빠른 참조 (Quick Reference)

## 설치 및 실행

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. API 키 설정
cp .env.example .env
# .env 파일 편집

# 3. 실행
python main.py
```

---

## 기본 사용법

```python
import asyncio
from main import DeepSearchEngine

async def main():
    engine = DeepSearchEngine()
    result = await engine.search("당신의 주제", verbose=True)
    print(result["report"])

asyncio.run(main())
```

---

## 결과 접근

```python
result["topic"]                          # 검색 주제
result["research_brief"]                 # 명확화된 브리프
result["iterations"]                     # 반복 횟수
result["compressed"]["key_findings"]     # 핵심 발견 (list)
result["compressed"]["confidence_score"] # 신뢰도 (0-1)
result["compressed"]["sources"]          # 출처 목록
result["report"]                         # 최종 마크다운 보고서
```

---

## 설정 변경

```python
from config import config

# 빠른 검색
config.max_supervisor_iterations = 2
config.max_concurrent_researchers = 2

# 깊이 있는 검색
config.max_supervisor_iterations = 5
config.max_concurrent_researchers = 5

# 저렴한 모델 사용
config.supervisor_model = "claude-3-5-haiku-20241022"
```

---

## 파일 구조

```
main.py              # 진입점
├─ state.py         # 상태 정의
├─ config.py        # 설정
├─ prompts.py       # 프롬프트
├─ search_tools.py  # 검색 도구
└─ llm_client.py    # LLM + 에이전트
```

---

## 문서

| 문서 | 대상 | 내용 |
|------|------|------|
| **README.md** | 모두 | 프로젝트 개요 |
| **GETTING_STARTED.md** | 초보자 | 5분 시작 가이드 |
| **ARCHITECTURE.md** | 개발자 | 기술 상세 |
| **PROJECT_SUMMARY.md** | 매니저 | 프로젝트 요약 |
| **QUICK_REFERENCE.md** | 모두 | 빠른 참조 (이것) |

---

## 에러 해결

### API Key Error
```bash
# .env 파일 확인
cat .env
# ANTHROPIC_API_KEY와 TAVILY_API_KEY 확인
```

### TimeoutError
```python
# search_backend 변경
config.search_backend = "duckduckgo"
```

### Token Limit
```python
# 반복 줄이기
config.max_supervisor_iterations = 2
```

---

## 성능 팁

| 목표 | 방법 |
|------|------|
| 🚀 **속도 향상** | 반복 줄이기, Haiku 모델 |
| 💰 **비용 절감** | Haiku 모델, DuckDuckGo 사용 |
| 📊 **품질 향상** | 반복 늘리기, Opus 모델 |
| ⚡ **균형** | Sonnet 모델, 반복 2-3회 |

---

## 예제 실행

```bash
python examples.py
```

6가지 예제:
1. 기본 사용법
2. 여러 주제 검색
3. 커스텀 설정
4. 결과 후처리
5. 두 주제 비교
6. 에러 처리

---

## API 키 얻기

### Anthropic Claude
```
https://console.anthropic.com/account/keys
```

### Tavily Search
```
https://tavily.com/dashboard
```

---

## 비용 계산

```
Claude 3.5 Sonnet:  $0.30-0.50 per search
Tavily Search:      $0.01-0.05 per search (또는 Pro: $200/월)
Total per search:   $0.35-1.00
```

---

## 자주 묻는 질문 (FAQ)

**Q: 어떤 모델을 사용해야 하나요?**
A: Claude 3.5 Sonnet (권장) 또는 Haiku (저비용)

**Q: 반복 횟수는 몇 회가 좋나요?**
A: 기본 2-3회, 깊이 있으면 5회

**Q: 최대 실행 시간은?**
A: 약 60-120초 (반복과 검색에 따라)

**Q: 결과를 저장할 수 있나요?**
A: 네, JSON으로 저장 가능 (examples.py 참고)

**Q: 커스텀 검색 백엔드를 추가할 수 있나요?**
A: 네, search_tools.py에 추가 가능

---

**더 자세한 정보는 README.md를 참고하세요.** 📚
