"""
Deep Search Engine 실제 테스트
"""
import asyncio
import json
from main import DeepSearchEngine

async def main():
    print("\n" + "="*70)
    print("🔍 Deep Search Engine 테스트 시작")
    print("="*70)
    
    # 엔진 초기화
    engine = DeepSearchEngine(search_backend="tavily")
    
    # 테스트 주제 (한국어)
    test_topic = "2024년 AI 에이전트 기술의 최신 동향"
    
    print(f"\n📝 검색 주제: {test_topic}")
    print("\n⏳ 검색 진행 중... (1-2분 소요)\n")
    
    try:
        # 검색 실행
        result = await engine.search(test_topic, verbose=True)
        
        # 결과 출력
        print("\n" + "="*70)
        print("✅ 검색 완료!")
        print("="*70)
        
        print(f"\n📊 통계:")
        print(f"  • 반복 횟수: {result['iterations']}")
        print(f"  • 수집된 노트: {len(result['notes'])}")
        print(f"  • 핵심 발견: {len(result['compressed'].get('key_findings', []))}")
        print(f"  • 검색 횟수: {len(result['search_history'])}")
        
        # 핵심 발견 출력
        findings = result['compressed'].get('key_findings', [])
        if findings:
            print(f"\n🎯 핵심 발견 ({len(findings)}개):")
            for i, finding in enumerate(findings[:3], 1):
                print(f"  {i}. {finding}")
        
        # 신뢰도 출력
        confidence = result['compressed'].get('confidence_score', 0)
        print(f"\n📈 신뢰도: {confidence:.1%}")
        
        # 최종 보고서 미리보기
        report = result['report']
        print(f"\n📄 최종 보고서 (처음 500자):")
        print("-" * 70)
        print(report[:500] + "...")
        print("-" * 70)
        
        # 결과 JSON으로 저장
        output = {
            "topic": result["topic"],
            "iterations": result["iterations"],
            "key_findings": findings[:5],
            "confidence": confidence,
            "sources_count": len(result['compressed'].get('sources', [])),
        }
        
        with open("test_result.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 결과가 test_result.json에 저장되었습니다.")
        
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
