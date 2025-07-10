# 🤖 AI 분석 에이전트 사용 가이드

## 개요
Somniorum Library의 AI 분석 에이전트는 OpenAI GPT-3.5-turbo를 활용하여 소설 파일을 분석하고, 기존 설정과의 충돌을 확인하며, 스토리 발전을 위한 추천을 제공합니다.

## 기능
- **📊 고급 텍스트 분석**: 인물, 세계관 요소, 이벤트 자동 추출
- **⚠️ 충돌 감지**: 기존 설정과의 충돌 자동 분석
- **💡 AI 추천**: 스토리 발전을 위한 구체적인 추천 사항
- **📖 스토리 구조 분석**: 갈등, 해결, 전개 속도 분석

## 설정 방법

### 1. OpenAI API 키 설정

AI 분석 기능을 사용하려면 OpenAI API 키가 필요합니다. 다음 방법 중 하나로 설정하세요:

#### 방법 1: 환경변수 설정 (권장)

#### Windows (PowerShell)
```powershell
# 현재 세션에만 설정
$env:OPENAI_API_KEY="your_api_key_here"

# 또는 영구 설정 (시스템 환경변수)
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "your_api_key_here", "User")
```

#### Windows (Command Prompt)
```cmd
# 현재 세션에만 설정
set OPENAI_API_KEY=your_api_key_here

# 또는 영구 설정
setx OPENAI_API_KEY "your_api_key_here"
```

#### macOS/Linux
```bash
# 현재 세션에만 설정
export OPENAI_API_KEY="your_api_key_here"

# 영구 설정 (.bashrc 또는 .zshrc에 추가)
echo 'export OPENAI_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

#### 방법 2: .env 파일 생성 (프로젝트 루트에)

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 내용을 추가하세요:

```
OPENAI_API_KEY=your_api_key_here
```

#### 방법 3: 코드에서 직접 설정

`Agent/openai_agent.py` 파일에서 직접 API 키를 설정할 수 있습니다:

```python
import os
os.environ["OPENAI_API_KEY"] = "your_api_key_here"
```

## API 키 획득 방법

1. [OpenAI 웹사이트](https://platform.openai.com/)에 가입
2. API Keys 섹션으로 이동
3. "Create new secret key" 클릭
4. 생성된 키를 복사하여 위의 방법 중 하나로 설정

## 테스트

API 키 설정 후 다음 명령어로 테스트할 수 있습니다:

```bash
python test_openai_agent.py
```

또는

```bash
python debug_analysis.py
```

## 주의사항

- API 키는 민감한 정보이므로 공개 저장소에 업로드하지 마세요
- `.env` 파일은 `.gitignore`에 포함되어 있어야 합니다
- API 사용량에 따라 비용이 발생할 수 있습니다

## 필요한 패키지 설치
```bash
pip install openai streamlit
```

## 사용 방법

### 1. 애플리케이션 실행
```bash
cd frontend
streamlit run app.py
```

### 2. 파일 추가 및 AI 분석
1. 소설을 선택하거나 새로 생성
2. "파일 추가" 버튼 클릭
3. 파일 업로드 또는 직접 작성
4. "파일 저장" 버튼 클릭
5. **AI 분석이 자동으로 실행되어 중앙에 결과 표시**

## 분석 결과 예시

### 📋 요약
"새로운 파일에서 3명의 인물, 2개의 세계관 요소, 1개의 주요 이벤트를 발견했습니다. 기존 설정과의 충돌은 없으며, 8개의 추천 사항을 제공합니다."

### 👥 등장인물 분석
- **김철수** (주인공)
  - 성격: 열정적이고 도전적인 성격
  - 배경: 서울대학교 컴퓨터공학과 학생

### 🌍 세계관 요소
- **AI 기술** (기술)
  - 소설 작성을 도와주는 시스템

### 📅 주요 이벤트
- **AI 프로젝트 시작** (2024년 3월 15일, 중요도: 높음)
  - 김철수와 이영희가 새로운 AI 프로젝트를 시작

### 💡 AI 추천 사항
- **📝 스토리보드 발전 방향**
  - 김철수 캐릭터를 중심으로 한 새로운 챕터 구성
  - AI 기술의 윤리적 문제를 다루는 스토리 전개

- **👤 인물 설정 보완**
  - 김철수의 과거 경험과 동기 구체화
  - 이영희와의 관계 발전 방향 설정

## API 사용량 및 비용

### GPT-3.5-turbo 요금 (2024년 기준)
- 입력 토큰: $0.0015 / 1K 토큰
- 출력 토큰: $0.002 / 1K 토큰

### 예상 비용 (파일당)
- 일반적인 소설 파일 (1000자): 약 $0.01-0.02
- 긴 소설 파일 (5000자): 약 $0.05-0.10

## 문제 해결

### 1. API 키 오류
```
ValueError: OpenAI API 키가 필요합니다.
```
**해결**: 환경 변수 `OPENAI_API_KEY`를 설정하거나 API 키를 직접 전달하세요.

### 2. API 호출 실패
```
분석 중 오류가 발생했습니다: API 호출 실패
```
**해결**: 
- 인터넷 연결 확인
- API 키 유효성 확인
- OpenAI 계정 크레딧 확인

### 3. 분석 결과가 표시되지 않음
**해결**:
- 파일 저장 후 페이지 새로고침
- 브라우저 개발자 도구에서 오류 확인

## 고급 설정

### Agent 설정 커스터마이징
`Agent/config.py` 파일에서 다음 설정을 조정할 수 있습니다:

```python
# 분석 설정
"max_characters_per_analysis": 10,  # 최대 분석 인물 수
"max_world_elements_per_analysis": 15,  # 최대 분석 세계관 요소 수

# 충돌 감지 설정
"character_name_similarity_threshold": 0.8,  # 인물 이름 유사도 임계값

# 추천 설정
"max_storyboard_suggestions": 5,  # 최대 스토리보드 추천 수
```

## 지원 및 문의

문제가 발생하거나 개선 사항이 있으시면 이슈를 등록해주세요.

---

**참고**: 이 AI 에이전트는 OpenAI API를 사용하므로 인터넷 연결이 필요하며, API 사용량에 따른 비용이 발생할 수 있습니다. 
