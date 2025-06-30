"""
Agent 설정 관리 클래스
"""

class AgentConfig:
    """
    AI 분석 에이전트의 설정을 관리하는 클래스
    """
    
    def __init__(self):
        # 분석 설정
        self.analysis_settings = {
            "max_characters_per_analysis": 10,  # 한 번에 분석할 최대 인물 수
            "max_world_elements_per_analysis": 15,  # 한 번에 분석할 최대 세계관 요소 수
            "max_events_per_analysis": 20,  # 한 번에 분석할 최대 이벤트 수
            "min_character_name_length": 2,  # 최소 인물 이름 길이
            "context_window_size": 50,  # 문맥 분석 윈도우 크기
        }
        
        # 충돌 감지 설정
        self.conflict_detection = {
            "character_name_similarity_threshold": 0.8,  # 인물 이름 유사도 임계값
            "world_setting_keyword_overlap_threshold": 3,  # 세계관 설정 키워드 겹침 임계값
            "timeline_event_similarity_threshold": 5,  # 타임라인 이벤트 유사도 임계값
            "date_conflict_tolerance_days": 1,  # 날짜 충돌 허용 오차 (일)
        }
        
        # 추천 설정
        self.recommendation_settings = {
            "max_storyboard_suggestions": 5,  # 최대 스토리보드 추천 수
            "max_character_suggestions": 5,  # 최대 인물 추천 수
            "max_world_setting_suggestions": 5,  # 최대 세계관 설정 추천 수
            "max_timeline_suggestions": 5,  # 최대 타임라인 추천 수
            "suggestion_priority_threshold": 0.6,  # 추천 우선순위 임계값
        }
        
        # 출력 설정
        self.output_settings = {
            "include_detailed_analysis": True,  # 상세 분석 포함 여부
            "include_conflict_details": True,  # 충돌 상세 정보 포함 여부
            "include_recommendation_reasons": True,  # 추천 이유 포함 여부
            "max_report_length": 2000,  # 최대 리포트 길이
        }
    
    def get_analysis_setting(self, key: str, default=None):
        """분석 설정 값 가져오기"""
        return self.analysis_settings.get(key, default)
    
    def get_conflict_detection_setting(self, key: str, default=None):
        """충돌 감지 설정 값 가져오기"""
        return self.conflict_detection.get(key, default)
    
    def get_recommendation_setting(self, key: str, default=None):
        """추천 설정 값 가져오기"""
        return self.recommendation_settings.get(key, default)
    
    def get_output_setting(self, key: str, default=None):
        """출력 설정 값 가져오기"""
        return self.output_settings.get(key, default)
    
    def update_analysis_setting(self, key: str, value):
        """분석 설정 업데이트"""
        if key in self.analysis_settings:
            self.analysis_settings[key] = value
    
    def update_conflict_detection_setting(self, key: str, value):
        """충돌 감지 설정 업데이트"""
        if key in self.conflict_detection:
            self.conflict_detection[key] = value
    
    def update_recommendation_setting(self, key: str, value):
        """추천 설정 업데이트"""
        if key in self.recommendation_settings:
            self.recommendation_settings[key] = value
    
    def update_output_setting(self, key: str, value):
        """출력 설정 업데이트"""
        if key in self.output_settings:
            self.output_settings[key] = value
    
    def get_all_settings(self) -> dict:
        """모든 설정을 딕셔너리로 반환"""
        return {
            "analysis_settings": self.analysis_settings.copy(),
            "conflict_detection": self.conflict_detection.copy(),
            "recommendation_settings": self.recommendation_settings.copy(),
            "output_settings": self.output_settings.copy()
        }
    
    def load_settings_from_file(self, file_path: str):
        """파일에서 설정 로드"""
        try:
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                
            if 'analysis_settings' in settings:
                self.analysis_settings.update(settings['analysis_settings'])
            if 'conflict_detection' in settings:
                self.conflict_detection.update(settings['conflict_detection'])
            if 'recommendation_settings' in settings:
                self.recommendation_settings.update(settings['recommendation_settings'])
            if 'output_settings' in settings:
                self.output_settings.update(settings['output_settings'])
                
        except Exception as e:
            print(f"설정 파일 로드 오류: {e}")
    
    def save_settings_to_file(self, file_path: str):
        """설정을 파일에 저장"""
        try:
            import json
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.get_all_settings(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"설정 파일 저장 오류: {e}") 