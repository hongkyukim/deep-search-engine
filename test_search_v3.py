"""
Deep Search Engine 최종 테스트
"""
import asyncio
import json
from main import DeepSearchEngine
from config import config

async def main():
    print("\n" + "="*70)
    print("🔍 Deep Search Engine 최종 테스트")
    print("="*70)
    
    # 설정 확인
    print(f"\n⚙️ 최종 설정:")
    print(f"  • 감독자 모델: {config.supervisor_model}")
    print(f"  • 연구원 모델: {config.researcher_model}")
    print(f"  • 압축 모델: {config.compression_model}")
    print(f"  • 검색 백엔드: {config.search_backend}")
    
    # 빠른 테스트
    config.max_supervisor_iterations = 2
    config.max_concurrent_researchers = 2
    
    engine = DeepSearchEngine(search_backend="tavily")
    
    test_topic = "Python AI 에이전트 프레임워크"
    
    print(f"\n📝 검색 주제: {test_topic}")
    print("\n⏳ 실제 검색 실행 중...\n")
    
    try:
        result = await engine.search(test_topic, verbose=True)
        
        print("\n" + "="*70)
        print("✅ 검색 완료!")
        print("="*70)
        
        print(f"\n📊 최종 결과:")
        print(f"  • 반복 횟수: {result['iterations']}")
        print(f"  • 수집된 데이터: {len(result['notes'])} 개")
        print(f"  • 핵심 발견: {len(result['compressed'].get('key_findings', []))} 개")
        print(f"  • 검색 요청: {len(result['search_history'])} 회")
        print(f"  • 신뢰도: {result['compressed'].get('confidence_score', 0):.1%}")
        
        findings = result['compressed'].get('key_findings', [])
        if findings:
            print(f"\n🎯 발견된 주요 정보:")
            for i, finding in enumerate(findings[:3], 1):
                print(f"  {i}. {finding[:80]}...")
        
        print(f"\n✅ 최종 보고서 생성 완료")
        print(f"   길이: {len(result['report'])} 자")
        
        # 결과 저장
        with open("final_test_result.json", "w", encoding="utf-8") as f:
            json.dump({
                "topic": result["topic"],
                "status": "success",
                "iterations": result["iterations"],
                "key_findings_count": len(findings),
                "confidence": result['compressed'].get('confidence_score', 0),
                "search_requests": len(result['search_history'])
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 결과 저장 완료: final_test_result.json")
        
    except Exception as e:
        print(f"\n❌ 에러: {type(e).__name__}")
        print(f"   {str(e)[:200]}")
        
        with open("final_test_result.json", "w", encoding="utf-8") as f:
            json.dump({
                "topic": test_topic,
                "status": "error",
                "error": str(e)[:200]
            }, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
