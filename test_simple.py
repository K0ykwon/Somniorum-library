#!/usr/bin/env python3
"""
간단한 OpenAI Agent 테스트
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Agent 모듈 import
sys.path.append(str(Path(__file__).parent))
from Agent import OpenAINovelAnalysisAgent

def test_simple():
    """간단한 테스트"""
    
    print("🧪 간단한 OpenAI Agent 테스트")
    print("=" * 50)
    
    # API 키 확인
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ API 키가 설정되지 않았습니다.")
        return
    
    print(f"✅ API 키 확인: {api_key[:20]}...")
    
    # 테스트용 소설 내용
    test_content = """
    김철수는 서울대학교에 다니는 대학생이다. 그는 컴퓨터공학을 전공하고 있으며, 
    프로그래밍에 대한 열정이 넘친다. 그의 친구인 이영희는 같은 학과의 학생으로, 
    항상 김철수와 함께 프로젝트를 진행한다.
    """
    
    try:
        # Agent 초기화
        print("🔧 Agent 초기화 중...")
        agent = OpenAINovelAnalysisAgent()
        print("✅ Agent 초기화 완료")
        
        # 파일 분석 수행
        print("\n📊 분석 시작...")
        analysis_result = agent.analyze_new_file("테스트소설", "테스트파일.txt", test_content)
        
        if "error" in analysis_result:
            print(f"❌ 분석 오류: {analysis_result['error']}")
            return
        
        print("✅ 분석 완료")
        
        # 분석 결과 구조 확인
        print(f"\n📋 분석 결과 구조:")
        print(f"- 키 개수: {len(analysis_result)}")
        print(f"- 키 목록: {list(analysis_result.keys())}")
        
        if 'content_analysis' in analysis_result:
            content_analysis = analysis_result['content_analysis']
            print(f"- content_analysis 키: {list(content_analysis.keys())}")
            
            if 'characters' in content_analysis:
                print(f"- 인물 수: {len(content_analysis['characters'])}")
                for char in content_analysis['characters']:
                    print(f"  - {char.get('name', 'Unknown')} ({char.get('role', '미정')})")
        
        if 'conflicts' in analysis_result:
            conflicts = analysis_result['conflicts']
            print(f"- 충돌 수: {sum(len(conflicts.get(key, [])) for key in ['character_conflicts', 'world_setting_conflicts', 'timeline_conflicts'])}")
        
        if 'recommendations' in analysis_result:
            recommendations = analysis_result['recommendations']
            print(f"- 추천 수: {sum(len(recommendations.get(key, [])) for key in ['storyboard_suggestions', 'character_suggestions', 'world_setting_suggestions', 'timeline_suggestions'])}")
        
        if 'summary' in analysis_result:
            print(f"- 요약: {analysis_result['summary']}")
        
        print("\n🎉 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple() 