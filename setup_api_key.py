#!/usr/bin/env python3
"""
OpenAI API 키 설정 도구
"""

import os
import sys
from pathlib import Path

def setup_api_key():
    """API 키 설정"""
    
    print("🔑 OpenAI API 키 설정 도구")
    print("=" * 50)
    
    # 현재 API 키 확인
    current_key = os.getenv("OPENAI_API_KEY")
    if current_key:
        print(f"✅ 현재 설정된 API 키: {current_key[:10]}...")
        response = input("새로운 API 키로 변경하시겠습니까? (y/N): ")
        if response.lower() != 'y':
            print("설정을 취소했습니다.")
            return
    
    # API 키 입력
    print("\n📝 OpenAI API 키를 입력하세요:")
    print("(API 키는 sk-로 시작하는 문자열입니다)")
    api_key = input("API 키: ").strip()
    
    if not api_key:
        print("❌ API 키가 입력되지 않았습니다.")
        return
    
    if not api_key.startswith("sk-"):
        print("❌ 올바른 OpenAI API 키 형식이 아닙니다. (sk-로 시작해야 합니다)")
        return
    
    # 환경변수 설정
    os.environ["OPENAI_API_KEY"] = api_key
    
    # .env 파일 생성
    env_file = Path(".env")
    try:
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(f"OPENAI_API_KEY={api_key}\n")
        print(f"✅ .env 파일에 API 키가 저장되었습니다.")
    except Exception as e:
        print(f"⚠️ .env 파일 생성 실패: {e}")
    
    # 테스트
    print("\n🧪 API 키 테스트 중...")
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        # 간단한 모델 목록 조회로 API 키 유효성 확인
        models = client.models.list()
        print("✅ API 키가 유효합니다!")
        print(f"📊 사용 가능한 모델 수: {len(models.data)}")
        
    except Exception as e:
        print(f"❌ API 키 테스트 실패: {e}")
        print("API 키를 다시 확인해주세요.")
        return
    
    print("\n🎉 API 키 설정이 완료되었습니다!")
    print("\n다음 명령어로 테스트할 수 있습니다:")
    print("  python test_openai_agent.py")
    print("  python debug_analysis.py")
    print("\n또는 웹 애플리케이션을 실행하세요:")
    print("  cd frontend")
    print("  python app.py")

def check_api_key():
    """API 키 상태 확인"""
    
    print("🔍 API 키 상태 확인")
    print("=" * 30)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ API 키가 설정되지 않았습니다.")
        return False
    
    print(f"✅ API 키가 설정되어 있습니다: {api_key[:10]}...")
    
    # 유효성 테스트
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        models = client.models.list()
        print("✅ API 키가 유효합니다!")
        return True
    except Exception as e:
        print(f"❌ API 키 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        check_api_key()
    else:
        setup_api_key() 