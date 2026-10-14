"""
Deep Search Engine 실제 테스트 (수정 버전)
"""
import asyncio
import json
from main import DeepSearchEngine
from config import config

async def main():
    print("\n" + "="*70)
    print("🔍 Deep Search Engine 테스트 (수정 버전)")
    print("="*70)
    
    # 설정 확인
    print(f"\n⚙️ 설정:")
    print(f"  • 모델: {config.supervisor_model}")
    print(f"  • 검색: {config.search_backend}")
    print(f"  • 최대 반복: {config.max_supervisor_iterations}")
    
    # 빠른 테스트를 위해 반복 줄이기
    config.max_supervisor_iterations = 2
    config.max_concurrent_researchers = 2
    
    # 엔진 초기화
    engine = DeepSearchEngine(search_backend="tavily")
    
    # 테스트 주제
    test_topic = "AI 에이전트 기술"
    
    print(f"\n📝 검색 주제: {test_topic}")
    print("\n⏳ 검색 진행 중...\n")
    
    try:
        # 검색 실행
        result = await engine.search(test_topic, verbose=True)
        
        # 결과 출력
        print("\n" + "="*70)
        print("✅ 검색 완료!")
        print("="*70)
        
        print(f"\n📊 결과 통계:")
        print(f"  • 반복 횟수: {result['iterations']}")
        print(f"  • 수집된 노트: {len(result['notes'])}")
        print(f"  • 핵심 발견: {len(result['compressed'].get('key_findings', []))}")
        print(f"  • 검색 횟수: {len(result['search_history'])}")
        
        # 핵심 발견 출력
        findings = result['compressed'].get('key_findings', [])
        if findings:
            print(f"\n🎯 핵심 발견 ({len(findings)}개):")
            for i, finding in enumerate(findings[:5], 1):
                print(f"  {i}. {finding[:100]}...")
        
        # 신뢰도
        confidence = result['compressed'].get('confidence_score', 0)
        print(f"\n📈 신뢰도: {confidence:.1%}")
        
        # 최종 보고서 미리보기
        report = result['report']
        if report and not report.startswith("[LLM Error"):
            print(f"\n📄 최종 보고서 (처음 300자):")
            print("-" * 70)
            print(report[:300] + "...")
            print("-" * 70)
        else:
            print("\n❌ 보고서 생성 실패")
        
        # 결과 저장
        output = {
            "topic": result["topic"],
            "iterations": result["iterations"],
            "key_findings": findings[:3],
            "confidence": confidence,
            "sources_count": len(result['compressed'].get('sources', [])),
            "status": "success"
        }
        
        with open("test_result_v2.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 결과가 test_result_v2.json에 저장되었습니다.")
        
    except Exception as e:
        print(f"\n❌ 에러 발생: {type(e).__name__}: {e}")
        
        output = {
            "topic": test_topic,
            "status": "error",
            "error": str(e)
        }
        
        with open("test_result_v2.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
