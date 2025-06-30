import openai
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from .utils import DatabaseManager
from .config import AgentConfig
from dotenv import load_dotenv
load_dotenv()

class OpenAINovelAnalysisAgent:
    """
    OpenAI API를 활용한 소설 파일 분석 에이전트
    """
    
    def __init__(self, api_key: str = None, database_path: str = "Database"):
        self.database_path = Path(database_path)
        self.db_manager = DatabaseManager(database_path)
        self.config = AgentConfig()
        
        # OpenAI API 키 설정
        if api_key:
            self.client = openai.OpenAI(api_key=api_key)
        elif os.getenv("OPENAI_API_KEY"):
            self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        else:
            raise ValueError("OpenAI API 키가 필요합니다. 환경변수 OPENAI_API_KEY를 설정하거나 api_key 매개변수를 전달하세요.")
    
    def analyze_new_file(self, novel_name: str, file_name: str, file_content: str, progress_callback=None) -> Dict[str, Any]:
        """
        OpenAI를 사용하여 새로 추가된 파일을 분석하고 결과를 반환
        
        Args:
            novel_name: 소설 이름
            file_name: 파일 이름
            file_content: 파일 내용
            progress_callback: 진행 메시지를 전달할 콜백 함수 (선택)
        
        Returns:
            분석 결과 딕셔너리
        """
        try:
            if progress_callback:
                progress_callback(f"🔍 분석 시작: {file_name}")
            print(f"🔍 분석 시작: {file_name}")
            
            # 1. 기존 데이터베이스 정보 수집
            existing_data = self._collect_existing_data(novel_name)
            msg = f"📊 기존 데이터 수집 완료: {len(existing_data)} 항목"
            if progress_callback:
                progress_callback(msg)
            print(msg)
            
            # 2. OpenAI를 사용한 고급 분석
            if progress_callback:
                progress_callback("🤖 OpenAI 분석 시작...")
            print("🤖 OpenAI 분석 시작...")
            if progress_callback:
                progress_callback("🤖 OpenAI API 호출 중...")
            content_analysis = self._analyze_with_openai(file_content, existing_data)
            if progress_callback:
                progress_callback("✅ OpenAI 응답 수신")
            msg = f"📋 파싱된 결과: {len(content_analysis)} 항목"
            if progress_callback:
                progress_callback(msg)
            print("✅ 내용 분석 완료: {} 항목".format(len(content_analysis)))
            if progress_callback:
                progress_callback(f"✅ 내용 분석 완료: {len(content_analysis)} 항목")
            
            # 3. 충돌 분석
            if progress_callback:
                progress_callback("⚠️ 충돌 분석 시작...")
            print("⚠️ 충돌 분석 시작...")
            if progress_callback:
                progress_callback("🤖 충돌 분석 OpenAI API 호출 중...")
            conflicts = self._analyze_conflicts_with_openai(content_analysis, existing_data)
            if progress_callback:
                progress_callback("✅ 충돌 분석 OpenAI 응답 수신")
            msg = f"📋 충돌 분석 결과: {len(conflicts)} 항목"
            if progress_callback:
                progress_callback(msg)
            print(f"✅ 충돌 분석 완료: {sum(len(v) for v in conflicts.values())}개 충돌")
            if progress_callback:
                progress_callback(f"✅ 충돌 분석 완료: {sum(len(v) for v in conflicts.values())}개 충돌")
            
            # 4. 추천 생성
            if progress_callback:
                progress_callback("💡 추천 생성 시작...")
            print("💡 추천 생성 시작...")
            if progress_callback:
                progress_callback("🤖 추천 생성 OpenAI API 호출 중...")
            recommendations = self._generate_recommendations_with_openai(content_analysis, existing_data, novel_name)
            if progress_callback:
                progress_callback("✅ 추천 생성 OpenAI 응답 수신")
            msg = f"📋 추천 생성 결과: {len(recommendations)} 항목"
            if progress_callback:
                progress_callback(msg)
            print(f"✅ 추천 생성 완료: {sum(len(v) for v in recommendations.values())}개 추천")
            if progress_callback:
                progress_callback(f"✅ 추천 생성 완료: {sum(len(v) for v in recommendations.values())}개 추천")
            
            # 5. 분석 결과 종합
            if progress_callback:
                progress_callback("📋 결과 종합 중...")
            print("📋 결과 종합 중...")
            analysis_result = {
                "file_name": file_name,
                "novel_name": novel_name,
                "content_analysis": content_analysis,
                "conflicts": conflicts,
                "recommendations": recommendations,
                "summary": self._generate_summary_with_openai(content_analysis, conflicts, recommendations)
            }
            if progress_callback:
                progress_callback("🤖 요약 생성 OpenAI API 호출 중...")
            if progress_callback:
                progress_callback("✅ 요약 생성 OpenAI 응답 수신")
            print("🎉 분석 완료!")
            if progress_callback:
                progress_callback("🎉 분석 완료!")
            return analysis_result
            
        except Exception as e:
            msg = f"❌ 분석 오류: {e}"
            if progress_callback:
                progress_callback(msg)
            print(msg)
            return {
                "error": f"분석 중 오류가 발생했습니다: {str(e)}",
                "file_name": file_name,
                "novel_name": novel_name
            }
    
    def _collect_existing_data(self, novel_name: str) -> Dict[str, Any]:
        """기존 데이터베이스 정보 수집"""
        return {
            "characters": self.db_manager.get_characters(novel_name),
            "world_settings": self.db_manager.get_world_settings(novel_name),
            "timeline_events": self.db_manager.get_timeline_events(novel_name),
            "storyboards": self.db_manager.get_storyboards(novel_name)
        }
    
    def _analyze_with_openai(self, content: str, existing_data: Dict[str, Any]) -> Dict[str, Any]:
        """OpenAI를 사용한 고급 내용 분석"""
        
        system_prompt = """
        당신은 소설 분석 전문가입니다. 주어진 텍스트를 분석하여 다음 정보를 최대한 자세히 추출해주세요:

1. 등장인물: 이름, 역할, 성격, 외모, 말투, 가치관, 관계, 성장배경, 트라우마, 세부 특성 등
2. 세계관 요소: 마법, 기술, 사회 구조, 문화, 규칙, 역사, 상징, 금기, 신화, 정치, 경제, 환경 등 모든 세부 항목
3. 주요 이벤트 (시간, 장소, 참여자, 중요도)
4. 장소 정보
5. 주요 테마와 주제
6. 스토리 구조 분석

반드시 JSON만 반환하세요. 코드블록(\`\`\`) 없이, 설명, 주석, 기타 텍스트는 절대 포함하지 마세요."""

        user_prompt = f"""다음 소설 텍스트를 분석해주세요:

{content}

기존 설정 정보:
- 기존 인물: {json.dumps([char.get('name', '') for char in existing_data['characters']], ensure_ascii=False)}
- 기존 세계관: {json.dumps([world.get('name', '') for world in existing_data['world_settings']], ensure_ascii=False)}
- 기존 이벤트: {json.dumps([event.get('title', '') for event in existing_data['timeline_events']], ensure_ascii=False)}

분석 결과를 다음 JSON 형식으로 반환해주세요:
{{
    "characters": [
        {{"name": "인물명", "role": "역할", "personality": "성격", "background": "배경"}}
    ],
    "world_elements": [
        {{"name": "요소명", "category": "분류", "description": "설명"}}
    ],
    "events": [
        {{"date": "날짜", "title": "제목", "description": "설명", "importance": "중요도", "participants": ["참여자"]}}
    ],
    "locations": ["장소1", "장소2"],
    "themes": ["테마1", "테마2"],
    "story_structure": {{"conflict": "갈등", "resolution": "해결", "pacing": "전개속도"}}
}}
반드시 JSON만 반환하세요. 코드블록(\`\`\`) 없이, 설명, 주석, 기타 텍스트는 절대 포함하지 마세요."""

        system_prompt = system_prompt.strip() + "\n반드시 JSON만 반환하세요. 코드블록(\`\`\`) 없이, 설명, 주석, 기타 텍스트는 절대 포함하지 마세요."
        user_prompt = user_prompt.strip() + "\n반드시 JSON만 반환하세요. 코드블록(\`\`\`) 없이, 설명, 주석, 기타 텍스트는 절대 포함하지 마세요."
        try:
            print("🤖 OpenAI API 호출 중...")
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            print("✅ OpenAI 응답 수신")
            content = response.choices[0].message.content.strip()
            # 코드블록 제거
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            if not content:
                print("❌ OpenAI 응답이 비어 있습니다.")
                raise ValueError("OpenAI 응답이 비어 있습니다.")
            try:
                result = json.loads(content)
            except Exception as e:
                print("❌ OpenAI 응답 파싱 실패:", content)
                raise ValueError(f"OpenAI 응답 파싱 실패: {e}\n응답 내용: {content}")
            print(f"📋 파싱된 결과: {len(result)} 항목")
            return result
            
        except Exception as e:
            print(f"❌ OpenAI 분석 실패: {e}")
            raise
    
    def _analyze_conflicts_with_openai(self, content_analysis: Dict[str, Any], existing_data: Dict[str, Any]) -> Dict[str, Any]:
        """OpenAI를 사용한 모순(contradiction) 분석"""
        
        system_prompt = """
당신은 소설 내용의 모순(contradiction)을 분석하는 전문가입니다. 
다음 두 가지 유형의 모순을 찾아주세요:

1. 내부 모순: 제공된 소설 내용 내에서 서로 모순되는 부분
2. 외부 모순: 새로운 내용과 기존 설정 간의 논리적 모순

※ 단, 기존 DB(설정/인물/이벤트 등)에 없는 새로운 정보(신규 인물, 신규 설정, 신규 이벤트 등)는 모순이 아닙니다. 논리적으로 기존 정보와 충돌(모순)되는 경우만 모순으로 간주하세요.

각 모순의 심각도를 평가해주세요:
- 심각(🔴): 스토리 전체에 영향을 주는 핵심 모순
- 보통(🟡): 일부 설정이나 세부사항의 모순  
- 경미(🟢): 표현이나 설명의 작은 불일치
"""

        user_prompt = f"""다음 내용에서 모순을 분석해주세요:

새로운 내용:
{json.dumps(content_analysis, ensure_ascii=False, indent=2)}

기존 설정:
{json.dumps(existing_data, ensure_ascii=False, indent=2)}

모순 분석 결과를 다음 JSON 형식으로 반환해주세요:
{{
    "internal_contradictions": [
        {{
            "type": "내부 모순 유형 (인물/이벤트/세계관)",
            "description": "모순 내용 설명",
            "severity": "심각/보통/경미",
            "elements": ["모순되는 요소1", "모순되는 요소2"],
            "suggestion": "해결 방안"
        }}
    ],
    "external_contradictions": [
        {{
            "type": "외부 모순 유형 (인물/이벤트/세계관)",
            "description": "모순 내용 설명", 
            "severity": "심각/보통/경미",
            "new_element": "새로운 내용",
            "existing_element": "기존 설정",
            "suggestion": "해결 방안"
        }}
    ]
}}
반드시 JSON만 반환하세요. 코드블록(\`\`\`) 없이, 설명, 주석, 기타 텍스트는 절대 포함하지 마세요."""

        system_prompt = system_prompt.strip() + "\n반드시 JSON만 반환하세요. 코드블록(\`\`\`) 없이, 설명, 주석, 기타 텍스트는 절대 포함하지 마세요."
        user_prompt = user_prompt.strip() + "\n반드시 JSON만 반환하세요. 코드블록(\`\`\`) 없이, 설명, 주석, 기타 텍스트는 절대 포함하지 마세요."
        try:
            print("🤖 모순 분석 OpenAI API 호출 중...")
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            print("✅ 모순 분석 OpenAI 응답 수신")
            result = json.loads(response.choices[0].message.content)
            print(f"📋 모순 분석 결과: {len(result.get('internal_contradictions', [])) + len(result.get('external_contradictions', []))}개 모순")
            return result
            
        except Exception as e:
            print(f"❌ 모순 분석 OpenAI 실패: {e}")
            raise e
    
    def _generate_recommendations_with_openai(self, content_analysis: Dict[str, Any], existing_data: Dict[str, Any], novel_name: str) -> Dict[str, Any]:
        """OpenAI를 사용한 추천 생성"""
        
        system_prompt = """당신은 소설 창작 조언 전문가입니다. 새로운 내용을 바탕으로 스토리 발전을 위한 구체적인 추천을 제공해주세요."""

        user_prompt = f"""다음 내용을 바탕으로 소설 발전을 위한 추천을 생성해주세요:

새로운 내용:
{json.dumps(content_analysis, ensure_ascii=False, indent=2)}

기존 설정:
{json.dumps(existing_data, ensure_ascii=False, indent=2)}

소설명: {novel_name}

다음 카테고리별로 구체적인 추천을 제공해주세요:
1. 스토리보드 발전 방향
2. 인물 설정 보완 사항
3. 세계관 설정 확장
4. 타임라인 구성 개선

JSON 형식으로 반환해주세요:
{{
    "storyboard_suggestions": ["추천1", "추천2"],
    "character_suggestions": ["추천1", "추천2"],
    "world_setting_suggestions": ["추천1", "추천2"],
    "timeline_suggestions": ["추천1", "추천2"]
}}
반드시 JSON만 반환하세요. 코드블록(\`\`\`) 없이, 설명, 주석, 기타 텍스트는 절대 포함하지 마세요."""

        system_prompt = system_prompt.strip() + "\n반드시 JSON만 반환하세요. 코드블록(\`\`\`) 없이, 설명, 주석, 기타 텍스트는 절대 포함하지 마세요."
        user_prompt = user_prompt.strip() + "\n반드시 JSON만 반환하세요. 코드블록(\`\`\`) 없이, 설명, 주석, 기타 텍스트는 절대 포함하지 마세요."
        try:
            print("🤖 추천 생성 OpenAI API 호출 중...")
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            print("✅ 추천 생성 OpenAI 응답 수신")
            result = json.loads(response.choices[0].message.content)
            print(f"📋 추천 생성 결과: {len(result)} 항목")
            return result
            
        except Exception as e:
            print(f"❌ 추천 생성 OpenAI 실패: {e}")
            raise e  # 예외를 그대로 발생시킴
    
    def _generate_summary_with_openai(self, content_analysis: Dict[str, Any], conflicts: Dict[str, Any], recommendations: Dict[str, Any]) -> str:
        """OpenAI를 사용한 요약 생성"""
        
        system_prompt = """당신은 소설 분석 요약 전문가입니다. 분석 결과를 간결하고 명확하게 요약해주세요."""

        user_prompt = f"""다음 분석 결과를 요약해주세요:

내용 분석:
{json.dumps(content_analysis, ensure_ascii=False, indent=2)}

충돌 정보:
{json.dumps(conflicts, ensure_ascii=False, indent=2)}

추천 사항:
{json.dumps(recommendations, ensure_ascii=False, indent=2)}

한 문장으로 핵심을 요약해주세요."""

        system_prompt = system_prompt.strip() + "\n반드시 JSON만 반환하세요. 코드블록(\`\`\`) 없이, 설명, 주석, 기타 텍스트는 절대 포함하지 마세요."
        user_prompt = user_prompt.strip() + "\n반드시 JSON만 반환하세요. 코드블록(\`\`\`) 없이, 설명, 주석, 기타 텍스트는 절대 포함하지 마세요."
        try:
            print("🤖 요약 생성 OpenAI API 호출 중...")
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            print("✅ 요약 생성 OpenAI 응답 수신")
            result = response.choices[0].message.content.strip()
            print(f"📋 요약 결과: {result}")
            return result
            
        except Exception as e:
            print(f"❌ 요약 생성 OpenAI 실패: {e}")
            raise e  # 예외를 그대로 발생시킴
    
    def get_analysis_report(self, analysis_result: Dict[str, Any]) -> str:
        """
        분석 결과를 읽기 쉬운 형태로 변환
        
        Args:
            analysis_result: 분석 결과 딕셔너리
            
        Returns:
            포맷된 분석 리포트 문자열
        """
        if "error" in analysis_result:
            return f"❌ 오류: {analysis_result['error']}"
        
        report_parts = []
        
        # 헤더
        report_parts.append(f"# 📊 AI 분석 결과: {analysis_result['file_name']}")
        report_parts.append("")
        
        # 요약
        report_parts.append(f"## 📋 요약")
        report_parts.append(analysis_result['summary'])
        report_parts.append("")
        
        # 상세 분석
        content_analysis = analysis_result.get('content_analysis', {})
        
        if content_analysis.get('characters'):
            report_parts.append("## 👥 등장인물 분석")
            for char in content_analysis['characters']:
                report_parts.append(f"### {char.get('name', 'Unknown')}")
                report_parts.append(f"- **역할**: {char.get('role', '미정')}")
                report_parts.append(f"- **성격**: {char.get('personality', '미정')}")
                report_parts.append(f"- **배경**: {char.get('background', '미정')}")
                report_parts.append("")
        
        if content_analysis.get('world_elements'):
            report_parts.append("## 🌍 세계관 요소")
            for element in content_analysis['world_elements']:
                report_parts.append(f"### {element.get('name', 'Unknown')}")
                report_parts.append(f"- **분류**: {element.get('category', '기타')}")
                report_parts.append(f"- **설명**: {element.get('description', '')}")
                report_parts.append("")
        
        if content_analysis.get('events'):
            report_parts.append("## 📅 주요 이벤트")
            for event in content_analysis['events']:
                report_parts.append(f"### {event.get('title', 'Unknown')}")
                report_parts.append(f"- **날짜**: {event.get('date', '미정')}")
                report_parts.append(f"- **중요도**: {event.get('importance', '보통')}")
                report_parts.append(f"- **설명**: {event.get('description', '')}")
                report_parts.append("")
        
        # 충돌 정보
        conflicts = analysis_result.get('conflicts', {})
        if any(conflicts.values()):
            report_parts.append("## ⚠️ 발견된 충돌")
            
            if conflicts.get('character_conflicts'):
                report_parts.append("### 인물 충돌")
                for conflict in conflicts['character_conflicts']:
                    report_parts.append(f"- **{conflict.get('new_character', 'Unknown')}** ↔️ **{conflict.get('existing_character', 'Unknown')}**")
                    report_parts.append(f"  - {conflict.get('description', '')}")
                report_parts.append("")
            
            if conflicts.get('world_setting_conflicts'):
                report_parts.append("### 세계관 설정 충돌")
                for conflict in conflicts['world_setting_conflicts']:
                    report_parts.append(f"- **{conflict.get('new_element', 'Unknown')}** ↔️ **{conflict.get('existing_element', 'Unknown')}**")
                    report_parts.append(f"  - {conflict.get('description', '')}")
                report_parts.append("")
            
            if conflicts.get('timeline_conflicts'):
                report_parts.append("### 타임라인 충돌")
                for conflict in conflicts['timeline_conflicts']:
                    report_parts.append(f"- **{conflict.get('new_event', 'Unknown')}** ↔️ **{conflict.get('existing_event', 'Unknown')}**")
                    report_parts.append(f"  - {conflict.get('description', '')}")
                report_parts.append("")
        else:
            report_parts.append("## ✅ 충돌 없음")
            report_parts.append("새로 추가된 내용과 기존 설정 간 충돌이 발견되지 않았습니다.")
            report_parts.append("")
        
        # 추천 사항
        recommendations = analysis_result.get('recommendations', {})
        if any(recommendations.values()):
            report_parts.append("## 💡 AI 추천 사항")
            
            if recommendations.get('storyboard_suggestions'):
                report_parts.append("### 📝 스토리보드 발전 방향")
                for suggestion in recommendations['storyboard_suggestions']:
                    report_parts.append(f"- {suggestion}")
                report_parts.append("")
            
            if recommendations.get('character_suggestions'):
                report_parts.append("### 👤 인물 설정 보완")
                for suggestion in recommendations['character_suggestions']:
                    report_parts.append(f"- {suggestion}")
                report_parts.append("")
            
            if recommendations.get('world_setting_suggestions'):
                report_parts.append("### 🌍 세계관 설정 확장")
                for suggestion in recommendations['world_setting_suggestions']:
                    report_parts.append(f"- {suggestion}")
                report_parts.append("")
            
            if recommendations.get('timeline_suggestions'):
                report_parts.append("### 📅 타임라인 구성 개선")
                for suggestion in recommendations['timeline_suggestions']:
                    report_parts.append(f"- {suggestion}")
                report_parts.append("")
        
        return "\n".join(report_parts)
    
    def extract_recommendations_with_openai(self, analysis_result, db_data, character_format_example=None):
        """
        OpenAI를 활용해 분석 결과와 DB(인물/스토리보드)를 비교하여 추천 항목을 추출합니다.
        인물/씬 모두 'add'와 'update'로 분리하여 반환합니다.
        character_format_example: 인물 포맷 예시(dict 또는 str)
        """
        system_prompt = """
        당신은 소설 데이터베이스 관리 전문가입니다.
        아래 분석 결과와 기존 DB(인물/스토리보드)를 비교하여, 다음을 추출하세요:
        1. 인물: 제공된 인물 포맷에 맞춰 신규/수정/보완이 필요한 인물 추천 항목을 'add'와 'update'로 분리
        2. 씬: 추가/수정이 필요한 씬 정보를 json 형태로 'add'와 'update'로 분리
        각 항목별로 type(add/update), name, reason, data(포맷에 맞는 정보)를 포함하세요.
        결과는 반드시 아래 JSON 예시 포맷을 따르세요.
        """
        
        # 인물 포맷 예시
        if character_format_example is None:
            character_format_example = {
                "name": "홍길동",
                "role": "주인공",
                "personality": "용감하고 정의로움",
                "background": "조선시대 의적"
            }
        
        user_prompt = f"""
        [인물 포맷 예시]
        {json.dumps(character_format_example, ensure_ascii=False, indent=2)}

        [분석 결과]
        {json.dumps(analysis_result, ensure_ascii=False, indent=2)}

        [기존 DB]
        {json.dumps(db_data, ensure_ascii=False, indent=2)}

        [JSON 반환 예시]
        {{
            "character_recommendations": {{
                "add": [
                    {{"name": "홍길동", "reason": "신규 인물", "data": {json.dumps(character_format_example, ensure_ascii=False)}}}
                ],
                "update": [
                    {{"name": "임꺽정", "reason": "성격 정보 누락", "data": {json.dumps(character_format_example, ensure_ascii=False)}}}
                ]
            }},
            "storyboard_recommendations": {{
                "add": [
                    {{"target": "scene", "name": "씬4", "reason": "새로운 이벤트", "data": {{"title": "씬4", "description": "..."}}}}
                ],
                "update": [
                    {{"target": "scene", "name": "씬2", "reason": "내용 불일치", "data": {{"title": "씬2", "description": "..."}}}}
                ]
            }}
        }}
        """
        
        system_prompt = system_prompt.strip() + "\n반드시 JSON만 반환하세요. 코드블록(\`\`\`) 없이, 설명, 주석, 기타 텍스트는 절대 포함하지 마세요."
        user_prompt = user_prompt.strip() + "\n반드시 JSON만 반환하세요. 코드블록(\`\`\`) 없이, 설명, 주석, 기타 텍스트는 절대 포함하지 마세요."
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            result = json.loads(response.choices[0].message.content)
            # add/update가 없을 경우 빈 리스트로 보정
            for key in ["character_recommendations", "storyboard_recommendations"]:
                if key not in result:
                    result[key] = {"add": [], "update": []}
                else:
                    if "add" not in result[key]:
                        result[key]["add"] = []
                    if "update" not in result[key]:
                        result[key]["update"] = []
            return result
        except Exception as e:
            print(f"❌ 정보 추출 OpenAI 실패: {e}")
            return {
                "character_recommendations": {"add": [], "update": []},
                "storyboard_recommendations": {"add": [], "update": []}
            }

    def extract_new_storyboard_with_openai(self, analysis_result, storyboard_db_example):
        """
        OpenAI를 활용해 기존 스토리보드 DB와 분석 결과를 비교,
        추가해야 할 씬을 기존 DB와 동일한 포맷의 JSON 리스트로 추출
        """
        system_prompt = """
        당신은 소설 스토리보드 데이터 관리 전문가입니다.
        아래 기존 스토리보드와 소설 분석 결과를 비교해,
        기존 DB에 없는, 추가해야 할 씬만 기존 DB와 동일한 JSON 포맷으로 추출하세요.
        반드시 JSON 리스트만 반환하세요.
        """
        user_prompt = f"""
        [기존 스토리보드 예시]
        {json.dumps(storyboard_db_example, ensure_ascii=False, indent=2)}

        [소설 분석 결과]
        {json.dumps(analysis_result, ensure_ascii=False, indent=2)}

        [추가할 씬 JSON 리스트 예시]
        [
          {{
            "title": "새로운 씬",
            "description": "..."
          }}
        ]
        """
        system_prompt = system_prompt.strip() + "\n반드시 JSON만 반환하세요. 코드블록(\`\`\`) 없이, 설명, 주석, 기타 텍스트는 절대 포함하지 마세요."
        user_prompt = user_prompt.strip() + "\n반드시 JSON만 반환하세요. 코드블록(\`\`\`) 없이, 설명, 주석, 기타 텍스트는 절대 포함하지 마세요."
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            result = json.loads(response.choices[0].message.content)
            # --- 후처리: name→title 보정 ---
            for elem in result:
                if 'name' in elem and 'title' not in elem:
                    elem['title'] = elem['name']
                    del elem['name']
            return result
        except Exception as e:
            print(f"❌ 스토리보드 추가 추출 OpenAI 실패: {e}")
            return []

    def extract_new_characters_with_openai(self, analysis_result, character_db_example, character_format_example):
        """
        OpenAI를 활용해 기존 인물 DB와 분석 결과를 비교,
        추가해야 할 인물을 인물 포맷의 JSON 리스트로 추출
        """
        system_prompt = """
        당신은 소설 인물 데이터베이스 관리 전문가입니다.
        아래 기존 인물 DB와 소설 분석 결과를 비교해,
        기존 DB에 없는, 추가해야 할 인물만 반드시 아래 인물 포맷(character_format_example)에 맞는 JSON으로 추출하세요.
        반드시 JSON 리스트만 반환하세요.
        
        주의사항:
        1. 소설 분석 결과의 characters 배열에 있는 인물 정보를 최대한 활용하세요.
        2. 인물의 이름이 기존 DB에 없다면 무조건 추가하세요.
        3. 각 인물은 character_format_example의 모든 필드를 포함해야 하며, 정보가 없는 필드는 빈 문자열("")로 설정하세요.
        4. 인물의 이름은 반드시 포함해야 합니다.
        5. 지나가는 인물이라도 모두 추출하세요.
        """
        user_prompt = f"""
        [인물 포맷 예시]
        {json.dumps(character_format_example, ensure_ascii=False, indent=2)}

        [기존 인물 데이터]
        {json.dumps(character_db_example, ensure_ascii=False, indent=2)}

        [소설 분석 결과]
        {json.dumps(analysis_result.get('content_analysis', {}), ensure_ascii=False, indent=2)}

        [추가할 인물 JSON 리스트 예시]
        [
          {json.dumps(character_format_example, ensure_ascii=False, indent=2)}
        ]
        """
        system_prompt = system_prompt.strip() + "\n반드시 JSON만 반환하세요. 코드블록(\`\`\`) 없이, 설명, 주석, 기타 텍스트는 절대 포함하지 마세요."
        user_prompt = user_prompt.strip() + "\n반드시 JSON만 반환하세요. 코드블록(\`\`\`) 없이, 설명, 주석, 기타 텍스트는 절대 포함하지 마세요."
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            result = json.loads(response.choices[0].message.content)
            filtered = []
            existing_names = {char.get('name', '') or char.get('이름', '') for char in character_db_example}
            
            for char in result:
                # 이름이 없으면 제외
                name = char.get('name', '') or char.get('이름', '')
                if not name:
                    continue
                    
                # 이미 DB에 있는 이름이면 제외
                if name in existing_names:
                    continue
                    
                # character_format_example의 모든 필드가 있는지 확인하고, 없으면 빈 문자열로 설정
                for k in character_format_example.keys():
                    if k not in char:
                        char[k] = ""
                
                filtered.append(char)
            
            return filtered
        except Exception as e:
            print(f"❌ 인물 추가 추출 OpenAI 실패: {e}")
            return []

    def extract_new_world_elements_with_openai(self, analysis_result, world_db_example, category_list):
        """
        OpenAI를 활용해 기존 세계관 DB와 분석 결과를 비교,
        추가해야 할 세계관 요소를 기존 DB와 동일한 포맷의 JSON 리스트로 추출
        각 요소의 category는 category_list 중 하나만 사용
        인물/캐릭터 관련 항목은 world_elements에서 제외
        반드시 title 필드를 포함해야 하며, name이 있으면 title로 복사
        """
        system_prompt = """
        당신은 소설 세계관 데이터 관리 전문가입니다.
        아래 카테고리 리스트를 참고하여, 각 세계관 요소의 category는 반드시 리스트 중 하나만 사용하세요.
        단, 인물(캐릭터) 관련 항목은 반드시 제외하세요.
        각 세계관 요소는 반드시 title(설정명) 필드를 포함해야 합니다.
        category가 없거나 리스트에 없으면 '기타'로 설정하세요.
        title이 없으면 name을 title로 사용하세요.
        """
        user_prompt = f"""
        [카테고리 리스트]
        {json.dumps(category_list, ensure_ascii=False)}

        [기존 세계관 DB 예시]
        {json.dumps(world_db_example, ensure_ascii=False, indent=2)}

        [소설 분석 결과]
        {json.dumps(analysis_result, ensure_ascii=False, indent=2)}

        [추가할 세계관 요소 JSON 리스트 예시]
        [
          {{
            "title": "새로운 세계관 요소",
            "category": "카테고리 리스트 중 하나",
            "description": "..."
          }}
        ]
        """
        system_prompt = system_prompt.strip() + "\n반드시 JSON만 반환하세요. 코드블록(\`\`\`) 없이, 설명, 주석, 기타 텍스트는 절대 포함하지 마세요."
        user_prompt = user_prompt.strip() + "\n반드시 JSON만 반환하세요. 코드블록(\`\`\`) 없이, 설명, 주석, 기타 텍스트는 절대 포함하지 마세요."
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            result = json.loads(response.choices[0].message.content)
            filtered = []
            for elem in result:
                # name→title 변환 보강
                if 'title' not in elem and 'name' in elem:
                    elem['title'] = elem['name']
                # category 보정
                if 'category' not in elem or elem['category'] not in category_list:
                    elem['category'] = '기타'
                # 인물/캐릭터 관련 카테고리 제외
                cat = elem.get('category', '').lower()
                if cat in ['인물', '캐릭터', 'person', 'character']:
                    continue
                # title이 없거나 빈 값이면 제외
                if not elem.get('title'):
                    continue
                filtered.append(elem)
            return filtered
        except Exception as e:
            print(f"❌ 세계관 추가 추출 OpenAI 실패: {e}")
            return []

    def extract_new_timeline_with_openai(self, analysis_result, timeline_db_example):
        """
        OpenAI를 활용해 기존 타임라인 DB와 분석 결과를 비교,
        추가해야 할 타임라인 이벤트를 기존 DB와 동일한 포맷의 JSON 리스트로 추출
        각 이벤트에 explicit_events(bool) 필드를 포함
        """
        system_prompt = """
        당신은 소설 타임라인 데이터 관리 전문가입니다.
        아래 기존 타임라인 DB와 소설 분석 결과를 비교해,
        기존 DB에 없는, 추가해야 할 타임라인 이벤트만 기존 DB와 동일한 JSON 포맷으로 추출하세요.
        각 이벤트에는 반드시 explicit_events(boolean) 필드를 포함하세요. (명시적 이벤트면 true, 암묵적이면 false)
        '명시적'의 기준: 이벤트에 시간(날짜 등)이 명확히 명시되어 있으면 명시적(true), 그렇지 않으면 암묵적(false)으로 간주하세요.
        반드시 JSON 리스트만 반환하세요.
        """
        user_prompt = f"""
        [기존 타임라인 DB 예시]
        {json.dumps(timeline_db_example, ensure_ascii=False, indent=2)}

        [소설 분석 결과]
        {json.dumps(analysis_result, ensure_ascii=False, indent=2)}

        [추가할 타임라인 이벤트 JSON 리스트 예시]
        [
          {{
            "title": "새로운 이벤트",
            "date": "...",
            "description": "...",
            "importance": "...",
            "explicit_events": true
          }}
        ]
        """
        system_prompt = system_prompt.strip() + "\n반드시 JSON만 반환하세요. 코드블록(\`\`\`) 없이, 설명, 주석, 기타 텍스트는 절대 포함하지 마세요."
        user_prompt = user_prompt.strip() + "\n반드시 JSON만 반환하세요. 코드블록(\`\`\`) 없이, 설명, 주석, 기타 텍스트는 절대 포함하지 마세요."
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            result = json.loads(response.choices[0].message.content)
            # --- 후처리: name→title 보정, explicit_events 보정 ---
            for elem in result:
                if 'name' in elem and 'title' not in elem:
                    elem['title'] = elem['name']
                    del elem['name']
                # explicit_events가 없으면 False로 보정
                if 'explicit_events' not in elem:
                    elem['explicit_events'] = False
            return result
        except Exception as e:
            print(f"❌ 타임라인 추가 추출 OpenAI 실패: {e}")
            return []

class SomnniAI:
    """
    DB(인물, 세계관, 타임라인, 스토리보드 등) 기반 질의응답 에이전트
    """
    def __init__(self, database_path="Database"):
        from .utils import DatabaseManager
        self.db = DatabaseManager(database_path)

    def answer_query(self, novel_name: str, query: str) -> str:
        """
        자연어 질문(query)에 대해 DB에서 관련 정보를 찾아 OpenAI로 답변 생성
        """
        # DB에서 모든 정보 불러오기
        characters = self.db.get_characters(novel_name)
        world = self.db.get_world_settings(novel_name)
        timeline = self.db.get_timeline_events(novel_name)
        storyboards = self.db.get_storyboards(novel_name)
        # 간단한 키워드 매칭 기반 요약(향후 embedding 등으로 개선 가능)
        import re
        query_lc = query.lower()
        matched = []
        for char in characters:
            if any(re.search(re.escape(str(val)), query_lc, re.IGNORECASE) for val in char.values() if isinstance(val, str)):
                matched.append(f"[인물] {char.get('name','') or char.get('이름','')}: {char}")
        for w in world:
            if any(re.search(re.escape(str(val)), query_lc, re.IGNORECASE) for val in w.values() if isinstance(val, str)):
                matched.append(f"[세계관] {w.get('title','') or w.get('name','')}: {w}")
        for t in timeline:
            if any(re.search(re.escape(str(val)), query_lc, re.IGNORECASE) for val in t.values() if isinstance(val, str)):
                matched.append(f"[타임라인] {t.get('title','') or t.get('date','')}: {t}")
        for s in storyboards:
            if any(re.search(re.escape(str(val)), query_lc, re.IGNORECASE) for val in s.values() if isinstance(val, str)):
                matched.append(f"[스토리보드] {s.get('title','')}: {s}")
        if not matched:
            matched.append("DB에서 관련 정보를 찾을 수 없습니다. 질문을 더 구체적으로 입력해 주세요.")
        # OpenAI에 전달할 프롬프트 구성
        system_prompt = """
        당신은 소설 데이터베이스 기반 AI 비서입니다. 아래 DB 요약과 사용자의 질문을 참고하여, 친절하고 자연스러운 한국어로 답변하세요. DB 요약에 직접적으로 관련된 정보만 간결하게 답변하고, 불필요한 정보는 포함하지 마세요.
        """
        db_summary = "\n".join(matched)
        user_prompt = f"""
        [DB 요약]\n{db_summary}\n\n[질문]\n{query}\n\n[답변]"""
        try:
            from openai import OpenAI
            import os
            api_key = os.getenv("OPENAI_API_KEY")
            client = OpenAI(api_key=api_key) if api_key else self.client
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt.strip()},
                    {"role": "user", "content": user_prompt.strip()}
                ],
                temperature=0.3,
                max_tokens=800
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"❌ SomnniAI OpenAI 답변 생성 실패: {e}")
            # fallback: DB 요약만 반환
            return db_summary

__all__ = [
    'OpenAINovelAnalysisAgent',
    'SomnniAI',
]
