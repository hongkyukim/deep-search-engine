"""
Deep Search 사용 예제 모음
"""

import asyncio
import json
from main import DeepSearchEngine


async def example_1_basic():
    """예제 1: 기본 사용법"""

    print("\n" + "="*60)
    print("예제 1: 기본 사용법")
    print("="*60)

    engine = DeepSearchEngine()

    result = await engine.search(
        topic="Python 에이전트 프레임워크 비교",
        verbose=True
    )

    # 결과 출력
    print("\n📄 최종 보고서:")
    print(result["report"][:1000] + "...")  # 처음 1000자

    return result


async def example_2_multiple_searches():
    """예제 2: 여러 주제 검색"""

    print("\n" + "="*60)
    print("예제 2: 여러 주제 검색")
    print("="*60)

    engine = DeepSearchEngine()

    topics = [
        "LangChain의 주요 기능",
        "에이전트 기반 시스템 설계 패턴",
        "AI 리서치 자동화"
    ]

    results = {}
    for topic in topics:
        print(f"\n🔍 검색 중: {topic}")
        result = await engine.search(topic, verbose=False)
        results[topic] = {
            "iterations": result["iterations"],
            "findings": len(result["compressed"].get("key_findings", [])),
            "confidence": result["compressed"].get("confidence_score", 0)
        }

    # 결과 비교
    print("\n📊 검색 결과 비교:")
    for topic, stats in results.items():
        print(f"• {topic}")
        print(f"  - 반복: {stats['iterations']}")
        print(f"  - 발견: {stats['findings']} 개")
        print(f"  - 신뢰도: {stats['confidence']:.1%}")


async def example_3_custom_config():
    """예제 3: 커스텀 설정"""

    print("\n" + "="*60)
    print("예제 3: 커스텀 설정")
    print("="*60)

    from config import config

    # 설정 변경
    original_iterations = config.max_supervisor_iterations
    config.max_supervisor_iterations = 2  # 빠른 검색
    config.max_concurrent_researchers = 2

    engine = DeepSearchEngine(search_backend="tavily")

    result = await engine.search(
        topic="빠른 검색 테스트",
        verbose=True
    )

    print(f"\n⚡ 빠른 설정으로 {result['iterations']} 반복만 실행")

    # 원래 설정 복원
    config.max_supervisor_iterations = original_iterations


async def example_4_result_processing():
    """예제 4: 결과 후처리"""

    print("\n" + "="*60)
    print("예제 4: 결과 후처리")
    print("="*60)

    engine = DeepSearchEngine()

    result = await engine.search(
        topic="머신러닝 기초 개념",
        verbose=False
    )

    # 1. 핵심 발견 추출
    key_findings = result["compressed"].get("key_findings", [])
    print("\n🎯 핵심 발견:")
    for i, finding in enumerate(key_findings, 1):
        print(f"{i}. {finding}")

    # 2. 신뢰도 확인
    confidence = result["compressed"].get("confidence_score", 0)
    print(f"\n📈 신뢰도: {confidence:.1%}")

    # 3. 출처 분석
    sources = result["compressed"].get("sources", [])
    print(f"\n📚 출처: {len(sources)} 개")
    for source in sources[:3]:
        print(f"• {source.get('title', 'Untitled')} ({source.get('relevance', 'unknown')})")

    # 4. 정보 격차
    gaps = result["compressed"].get("gaps", "")
    if gaps:
        print(f"\n❓ 추가 정보 필요: {gaps}")

    # 5. 결과를 JSON으로 저장
    output = {
        "topic": result["topic"],
        "iterations": result["iterations"],
        "key_findings": key_findings,
        "confidence": confidence,
        "sources_count": len(sources),
        "gaps": gaps
    }

    with open("result_summary.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 결과가 result_summary.json에 저장되었습니다.")


async def example_5_comparison():
    """예제 5: 두 주제 비교 검색"""

    print("\n" + "="*60)
    print("예제 5: 두 주제 비교 검색")
    print("="*60)

    engine = DeepSearchEngine()

    # 두 주제 검색
    topic1 = "OpenAI GPT-4 모델"
    topic2 = "Anthropic Claude 모델"

    print(f"\n🔍 주제 1: {topic1}")
    result1 = await engine.search(topic1, verbose=False)

    print(f"\n🔍 주제 2: {topic2}")
    result2 = await engine.search(topic2, verbose=False)

    # 비교 분석
    print("\n📊 비교 분석:")
    print(f"{'주제':<20} {'반복':<10} {'발견':<10} {'신뢰도':<10}")
    print("-" * 50)

    for topic, result in [(topic1, result1), (topic2, result2)]:
        findings = len(result["compressed"].get("key_findings", []))
        confidence = result["compressed"].get("confidence_score", 0)
        print(f"{topic:<20} {result['iterations']:<10} {findings:<10} {confidence:<10.1%}")


async def example_6_error_handling():
    """예제 6: 에러 처리"""

    print("\n" + "="*60)
    print("예제 6: 에러 처리")
    print("="*60)

    engine = DeepSearchEngine()

    try:
        # 빈 주제
        result = await engine.search("", verbose=False)
        if not result:
            print("⚠️ 검색 실패: 빈 주제")
    except Exception as e:
        print(f"❌ 에러: {e}")

    try:
        # 일반적인 주제
        result = await engine.search(
            topic="안녕하세요",
            verbose=False
        )
        print("✅ 검색 성공")
        print(f"반복: {result['iterations']}")
    except Exception as e:
        print(f"❌ 에러: {e}")


async def main():
    """모든 예제 실행"""

    print("\n" + "="*60)
    print("Deep Search Engine - 예제 모음")
    print("="*60)

    # 실행할 예제 선택
    examples = {
        "1": ("기본 사용법", example_1_basic),
        "2": ("여러 주제 검색", example_2_multiple_searches),
        "3": ("커스텀 설정", example_3_custom_config),
        "4": ("결과 후처리", example_4_result_processing),
        "5": ("두 주제 비교", example_5_comparison),
        "6": ("에러 처리", example_6_error_handling),
    }

    print("\n실행할 예제를 선택하세요:")
    for key, (desc, _) in examples.items():
        print(f"{key}. {desc}")
    print("0. 모두 실행")

    # 사용자 입력 받기 (데모에서는 모두 실행)
    choice = "0"

    if choice == "0":
        # 모두 실행
        for key, (desc, func) in examples.items():
            try:
                await func()
            except Exception as e:
                print(f"\n❌ 예제 {key} 실행 실패: {e}")
    else:
        # 선택된 예제만 실행
        if choice in examples:
            _, func = examples[choice]
            await func()
        else:
            print("❌ 잘못된 선택")


if __name__ == "__main__":
    asyncio.run(main())
