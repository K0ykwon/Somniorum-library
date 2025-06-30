import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import datetime

def safe_filename(s):
    """
    문자열에서 한글, 영문, 숫자만 남기고 나머지는 _로 치환. 길이 제한(40자)
    """
    return re.sub(r'[^가-힣a-zA-Z0-9]', '_', str(s))[:40]

class DatabaseManager:
    """
    데이터베이스 파일들을 관리하는 클래스
    """
    
    def __init__(self, database_path: str = "Database"):
        self.database_path = Path(database_path)
    
    def get_characters(self, novel_name: str) -> List[Dict[str, Any]]:
        """소설의 인물 정보를 가져옴"""
        characters = []
        characters_dir = self.database_path / novel_name / 'characters'
        
        if characters_dir.exists():
            for file in characters_dir.glob('*.json'):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        character_data = json.load(f)
                        characters.append(character_data)
                except Exception as e:
                    print(f"인물 파일 읽기 오류 {file}: {e}")
        
        return characters
    
    def get_world_settings(self, novel_name: str) -> List[Dict[str, Any]]:
        """소설의 세계관 설정을 가져옴"""
        world_settings = []
        world_dir = self.database_path / novel_name / 'world'
        
        if world_dir.exists():
            for file in world_dir.glob('*.json'):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        world_data = json.load(f)
                        world_settings.append(world_data)
                except Exception as e:
                    print(f"세계관 설정 파일 읽기 오류 {file}: {e}")
        
        return world_settings
    
    def get_timeline_events(self, novel_name: str) -> List[Dict[str, Any]]:
        """소설의 타임라인 이벤트를 가져옴"""
        events = []
        timeline_dir = self.database_path / novel_name / 'Timeline'
        
        if timeline_dir.exists():
            for file in timeline_dir.glob('*.json'):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        timeline_data = json.load(f)
                        events.append(timeline_data)
                except Exception as e:
                    print(f"타임라인 파일 읽기 오류 {file}: {e}")
        
        return events
    
    def get_storyboards(self, novel_name: str) -> List[Dict[str, Any]]:
        """소설의 스토리보드를 가져옴"""
        storyboards = []
        storyboard_dir = self.database_path / novel_name / 'Storyboard'
        
        if storyboard_dir.exists():
            for file in storyboard_dir.glob('*.json'):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        storyboard_data = json.load(f)
                        storyboards.append(storyboard_data)
                except Exception as e:
                    print(f"스토리보드 파일 읽기 오류 {file}: {e}")
        
        return storyboards

    def save_world_setting(self, novel_name: str, world_element: dict):
        """
        세계관 요소를 DB에 저장
        같은 title(또는 name)이 이미 존재하면 해당 파일을 덮어쓰고, 없으면 새로 저장
        """
        world_dir = self.database_path / novel_name / 'world'
        world_dir.mkdir(parents=True, exist_ok=True)
        name = world_element.get('name') or world_element.get('title') or f"unknown_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        file_path = world_dir / f"world_{safe_filename(name)}.json"
        # 이미 같은 파일이 있으면 덮어쓰기, 없으면 새로 생성
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(world_element, f, ensure_ascii=False, indent=2)

    def save_timeline_event(self, novel_name: str, event: dict):
        """
        타임라인 이벤트를 DB에 저장
        """
        timeline_dir = self.database_path / novel_name / 'Timeline'
        timeline_dir.mkdir(parents=True, exist_ok=True)
        title = event.get('title') or event.get('date') or f"unknown_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        # explicit_events -> type 필드로 변환
        if 'explicit_events' in event:
            event['type'] = '명시적' if event['explicit_events'] else '암묵적'
        file_path = timeline_dir / f"timeline_{safe_filename(title)}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(event, f, ensure_ascii=False, indent=2)

    def save_character(self, novel_name: str, character: dict):
        """
        인물 정보를 DB에 저장
        같은 name(또는 '이름')이 이미 존재하면 해당 파일을 덮어쓰고, 없으면 새로 저장
        """
        char_dir = self.database_path / novel_name / 'characters'
        char_dir.mkdir(parents=True, exist_ok=True)
        name = character.get('name') or character.get('이름') or f"unknown_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        file_path = char_dir / f"character_{safe_filename(name)}.json"
        # 이미 같은 파일이 있으면 덮어쓰기, 없으면 새로 생성
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(character, f, ensure_ascii=False, indent=2)

    def save_storyboard(self, novel_name: str, storyboard: dict):
        """
        스토리보드(씬)를 DB에 저장
        """
        sb_dir = self.database_path / novel_name / 'Storyboard'
        sb_dir.mkdir(parents=True, exist_ok=True)
        title = storyboard.get('title') or f"unknown_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        file_path = sb_dir / f"storyboard_{safe_filename(title)}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(storyboard, f, ensure_ascii=False, indent=2)

class ContentAnalyzer:
    """
    텍스트 내용을 분석하는 클래스
    """
    
    def __init__(self):
        # 한국어 인명 패턴 (성+이름)
        self.korean_name_pattern = r'[가-힣]{2,4}\s*(?:씨|님|군|양)?'
        # 영어 인명 패턴
        self.english_name_pattern = r'[A-Z][a-z]+\s+[A-Z][a-z]+'
        # 역할 관련 키워드
        self.role_keywords = [
            '주인공', '히로인', '조연', '악역', '라이벌', '멘토', '친구', '가족',
            'protagonist', 'hero', 'heroine', 'villain', 'rival', 'mentor', 'friend', 'family'
        ]
        # 세계관 요소 키워드
        self.world_keywords = [
            '마법', '기술', '문명', '국가', '도시', '마을', '학교', '회사', '조직',
            'magic', 'technology', 'civilization', 'country', 'city', 'village', 'school', 'company', 'organization'
        ]
        # 시간 관련 키워드
        self.time_keywords = [
            '년', '월', '일', '시', '분', '초', '아침', '점심', '저녁', '밤',
            'year', 'month', 'day', 'hour', 'minute', 'second', 'morning', 'afternoon', 'evening', 'night'
        ]
    
    def analyze_content(self, content: str) -> Dict[str, Any]:
        """
        텍스트 내용을 분석하여 인물, 세계관 요소, 이벤트 등을 추출
        
        Args:
            content: 분석할 텍스트 내용
            
        Returns:
            분석 결과 딕셔너리
        """
        analysis_result = {
            "characters": self._extract_characters(content),
            "world_elements": self._extract_world_elements(content),
            "events": self._extract_events(content),
            "locations": self._extract_locations(content),
            "themes": self._extract_themes(content)
        }
        
        return analysis_result
    
    def _extract_characters(self, content: str) -> List[Dict[str, Any]]:
        """인물 정보 추출"""
        characters = []
        
        # 한국어 인명 찾기
        korean_names = re.findall(self.korean_name_pattern, content)
        # 영어 인명 찾기
        english_names = re.findall(self.english_name_pattern, content)
        
        all_names = list(set(korean_names + english_names))
        
        for name in all_names:
            if len(name.strip()) > 1:  # 의미있는 이름만
                character_info = {
                    "name": name.strip(),
                    "role": self._identify_character_role(content, name),
                    "description": self._extract_character_description(content, name),
                    "first_mention": self._find_first_mention(content, name)
                }
                characters.append(character_info)
        
        return characters
    
    def _extract_world_elements(self, content: str) -> List[Dict[str, Any]]:
        """세계관 요소 추출"""
        world_elements = []
        
        # 세계관 관련 키워드가 포함된 문장 찾기
        sentences = re.split(r'[.!?]', content)
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in self.world_keywords):
                element_info = {
                    "name": self._extract_element_name(sentence),
                    "description": sentence.strip(),
                    "category": self._categorize_world_element(sentence)
                }
                world_elements.append(element_info)
        
        return world_elements
    
    def _extract_events(self, content: str) -> List[Dict[str, Any]]:
        """이벤트 추출"""
        events = []
        
        # 시간 관련 키워드가 포함된 문장 찾기
        sentences = re.split(r'[.!?]', content)
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in self.time_keywords):
                event_info = {
                    "date": self._extract_date(sentence),
                    "description": sentence.strip(),
                    "participants": self._extract_event_participants(content, sentence)
                }
                events.append(event_info)
        
        return events
    
    def _extract_locations(self, content: str) -> List[str]:
        """장소 정보 추출"""
        # 간단한 장소 패턴 (도시, 마을, 건물 등)
        location_patterns = [
            r'[가-힣]+시',  # 서울시, 부산시 등
            r'[가-힣]+동',  # 강남동, 서초동 등
            r'[가-힣]+학교',  # 서울대학교 등
            r'[가-힣]+회사',  # 삼성전자 등
        ]
        
        locations = []
        for pattern in location_patterns:
            found = re.findall(pattern, content)
            locations.extend(found)
        
        return list(set(locations))
    
    def _extract_themes(self, content: str) -> List[str]:
        """주제 추출"""
        # 간단한 주제 키워드
        theme_keywords = [
            '사랑', '우정', '가족', '성장', '모험', '복수', '희생', '희망',
            'love', 'friendship', 'family', 'growth', 'adventure', 'revenge', 'sacrifice', 'hope'
        ]
        
        themes = []
        for keyword in theme_keywords:
            if keyword in content:
                themes.append(keyword)
        
        return themes
    
    def _identify_character_role(self, content: str, character_name: str) -> str:
        """인물의 역할 식별"""
        # 캐릭터 이름 주변 문맥에서 역할 키워드 찾기
        name_index = content.find(character_name)
        if name_index != -1:
            # 이름 주변 50자 내에서 역할 키워드 찾기
            start = max(0, name_index - 50)
            end = min(len(content), name_index + len(character_name) + 50)
            context = content[start:end]
            
            for keyword in self.role_keywords:
                if keyword in context:
                    return keyword
        
        return "미정"
    
    def _extract_character_description(self, content: str, character_name: str) -> str:
        """인물 설명 추출"""
        # 캐릭터 이름이 처음 등장하는 문장 찾기
        sentences = re.split(r'[.!?]', content)
        
        for sentence in sentences:
            if character_name in sentence:
                return sentence.strip()
        
        return ""
    
    def _find_first_mention(self, content: str, character_name: str) -> int:
        """인물의 첫 등장 위치 찾기"""
        return content.find(character_name)
    
    def _extract_element_name(self, sentence: str) -> str:
        """세계관 요소의 이름 추출"""
        # 간단한 추출 로직 (첫 번째 명사구)
        words = sentence.split()
        if words:
            return words[0]
        return "Unknown"
    
    def _categorize_world_element(self, sentence: str) -> str:
        """세계관 요소 분류"""
        if any(keyword in sentence.lower() for keyword in ['마법', 'magic']):
            return "마법"
        elif any(keyword in sentence.lower() for keyword in ['기술', 'technology']):
            return "기술"
        elif any(keyword in sentence.lower() for keyword in ['국가', 'country']):
            return "정치"
        else:
            return "기타"
    
    def _extract_date(self, sentence: str) -> str:
        """날짜 정보 추출"""
        # 간단한 날짜 패턴
        date_patterns = [
            r'\d{4}년\s*\d{1,2}월\s*\d{1,2}일',
            r'\d{1,2}월\s*\d{1,2}일',
            r'\d{1,2}일',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, sentence)
            if match:
                return match.group()
        
        return ""
    
    def _extract_event_participants(self, content: str, event_sentence: str) -> List[str]:
        """이벤트 참여자 추출"""
        participants = []
        
        # 이벤트 문장에서 인명 찾기
        korean_names = re.findall(self.korean_name_pattern, event_sentence)
        english_names = re.findall(self.english_name_pattern, event_sentence)
        
        participants.extend(korean_names)
        participants.extend(english_names)
        
        return list(set(participants))

class RecommendationEngine:
    """
    추천 옵션을 생성하는 클래스
    """
    
    def __init__(self):
        self.storyboard_templates = [
            "새로운 챕터 추가: {theme}를 중심으로 한 스토리 전개",
            "씬 구성: {character}의 {action} 장면 추가",
            "갈등 요소: {conflict}를 통한 스토리 발전"
        ]
        
        self.character_templates = [
            "인물 설정 보완: {character}의 배경 스토리 추가",
            "관계 설정: {character1}과 {character2}의 관계 정의",
            "성격 개발: {character}의 성격 특징 구체화"
        ]
        
        self.world_setting_templates = [
            "세계관 규칙: {element}에 대한 상세 설정 추가",
            "환경 설정: {location}의 구체적인 묘사",
            "문화 요소: {culture}에 대한 설명 추가"
        ]
        
        self.timeline_templates = [
            "이벤트 순서: {event}의 정확한 시간 설정",
            "과거 배경: {background}에 대한 플래시백 추가",
            "미래 전개: {future}에 대한 복선 추가"
        ]
    
    def generate_storyboard_suggestions(self, content_analysis: Dict[str, Any], novel_name: str) -> List[str]:
        """스토리보드 추천 생성"""
        suggestions = []
        
        characters = content_analysis.get("characters", [])
        themes = content_analysis.get("themes", [])
        
        if characters:
            for character in characters[:3]:  # 상위 3명만
                suggestions.append(
                    f"'{character['name']}' 캐릭터를 중심으로 한 새로운 챕터 구성"
                )
        
        if themes:
            for theme in themes[:2]:  # 상위 2개 테마만
                suggestions.append(
                    f"'{theme}' 테마를 강화하는 스토리보드 추가"
                )
        
        # 기본 추천
        if not suggestions:
            suggestions.append("새로운 챕터를 추가하여 스토리 전개를 확장하세요")
            suggestions.append("주요 등장인물들의 개별 에피소드를 구성해보세요")
        
        return suggestions
    
    def generate_character_suggestions(self, content_analysis: Dict[str, Any], novel_name: str) -> List[str]:
        """인물 설정 추천 생성"""
        suggestions = []
        
        characters = content_analysis.get("characters", [])
        
        if characters:
            for character in characters:
                if character.get("role") == "미정":
                    suggestions.append(
                        f"'{character['name']}'의 역할을 명확히 정의하세요"
                    )
                
                if not character.get("description"):
                    suggestions.append(
                        f"'{character['name']}'의 상세한 배경 스토리를 추가하세요"
                    )
        
        # 관계 설정 추천
        if len(characters) >= 2:
            suggestions.append("등장인물들 간의 관계도를 작성하세요")
            suggestions.append("주요 인물들의 성격 차이점을 명확히 하세요")
        
        return suggestions
    
    def generate_world_setting_suggestions(self, content_analysis: Dict[str, Any], novel_name: str) -> List[str]:
        """세계관 설정 추천 생성"""
        suggestions = []
        
        world_elements = content_analysis.get("world_elements", [])
        locations = content_analysis.get("locations", [])
        
        if world_elements:
            for element in world_elements:
                suggestions.append(
                    f"'{element['name']}'에 대한 상세한 규칙과 설정을 추가하세요"
                )
        
        if locations:
            for location in locations[:3]:  # 상위 3개 장소만
                suggestions.append(
                    f"'{location}'의 구체적인 환경과 분위기를 묘사하세요"
                )
        
        # 기본 추천
        if not suggestions:
            suggestions.append("소설의 배경 세계관에 대한 기본 설정을 추가하세요")
            suggestions.append("마법이나 기술 체계에 대한 규칙을 정의하세요")
        
        return suggestions
    
    def generate_timeline_suggestions(self, content_analysis: Dict[str, Any], novel_name: str) -> List[str]:
        """타임라인 추천 생성"""
        suggestions = []
        
        events = content_analysis.get("events", [])
        
        if events:
            for event in events:
                if not event.get("date"):
                    suggestions.append(
                        f"'{event['description'][:20]}...' 이벤트의 정확한 시간을 설정하세요"
                    )
        
        # 기본 추천
        if not suggestions:
            suggestions.append("소설의 주요 이벤트들을 시간순으로 정리하세요")
            suggestions.append("과거 배경과 현재 상황의 연결점을 명확히 하세요")
        
        return suggestions 