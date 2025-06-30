#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
모순 분석 기능 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Agent.openai_agent import OpenAIAgent
import json

def test_contradiction_analysis():
    """모순 분석 기능 테스트"""
    
    # OpenAI Agent 초기화
    agent = OpenAIAgent()
    
    # 테스트용 내용 분석
    content_analysis = {
        "characters": [
            {
                "name": "윤재",
                "role": "주인공",
                "personality": "마법사",
                "background": "마법 학교 졸업생"
            },
            {
                "name": "윤재", 
                "role": "주인공",
                "personality": "마법을 못 쓴다",
                "background": "평범한 학생"
            }
        ],
        "world_elements": [
            {
                "name": "백록역",
                "category": "장소",
                "description": "평화로운 마을"
            },
            {
                "name": "백록역",
                "category": "장소", 
                "description": "전쟁터"
            }
        ],
        "events": [
            {
                "title": "마법 대회",
                "date": "아침",
                "importance": "중요",
                "description": "아침에 열린 마법 대회"
            },
            {
                "title": "마법 대회",
                "date": "저녁",
                "importance": "중요",
                "description": "저녁에 열린 마법 대회"
            }
        ]
    }
    
    # 기존 설정
    existing_data = {
        "characters": [
            {
                "name": "윤재",
                "role": "마법사",
                "personality": "강력한 마법사",
                "background": "마법 학교 최고 졸업생"
            }
        ],
        "world_elements": [
            {
                "name": "백록역",
                "category": "장소",
                "description": "평화로운 마을"
            }
        ]
    }
    
    print("🔍 모순 분석 테스트 시작...")
    
    try:
        # 모순 분석 실행
        result = agent._analyze_conflicts_with_openai(content_analysis, existing_data)
        
        print("✅ 모순 분석 완료!")
        print("\n📋 분석 결과:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 결과 검증
        internal_count = len(result.get('internal_contradictions', []))
        external_count = len(result.get('external_contradictions', []))
        
        print(f"\n📊 모순 개수:")
        print(f"- 내부 모순: {internal_count}개")
        print(f"- 외부 모순: {external_count}개")
        
        if internal_count > 0:
            print("\n🔍 내부 모순 예시:")
            for contradiction in result.get('internal_contradictions', [])[:2]:
                print(f"- {contradiction.get('type', '')}: {contradiction.get('description', '')}")
                print(f"  심각도: {contradiction.get('severity', '')}")
        
        if external_count > 0:
            print("\n🔍 외부 모순 예시:")
            for contradiction in result.get('external_contradictions', [])[:2]:
                print(f"- {contradiction.get('type', '')}: {contradiction.get('description', '')}")
                print(f"  심각도: {contradiction.get('severity', '')}")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")

if __name__ == "__main__":
    test_contradiction_analysis() 