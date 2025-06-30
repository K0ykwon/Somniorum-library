import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from .utils import DatabaseManager, ContentAnalyzer, RecommendationEngine
from .config import AgentConfig

class NovelAnalysisAgent:
    """
    소설 파일 추가 시 AI 분석을 수행하는 에이전트
    """
    
    def __init__(self, database_path: str = "Database"):
        self.database_path = Path(database_path)
        self.db_manager = DatabaseManager(database_path)
        self.analyzer = ContentAnalyzer()
        self.recommendation_engine = RecommendationEngine()
        self.config = AgentConfig()
    
    def analyze_new_file(self, novel_name: str, file_name: str, file_content: str) -> Dict[str, Any]:
        """
        새로 추가된 파일을 분석하고 결과를 반환
        
        Args:
            novel_name: 소설 이름
            file_name: 파일 이름
            file_content: 파일 내용
            
        Returns:
            분석 결과 딕셔너리
        """
        try:
            # 1. 파일 내용 분석
            content_analysis = self.analyzer.analyze_content(file_content)
            
            # 2. 기존 데이터베이스와 충돌 확인
            conflicts = self._check_conflicts(novel_name, content_analysis)
            
            # 3. 추천 옵션 생성
            recommendations = self._generate_recommendations(novel_name, content_analysis)
            
            # 4. 분석 결과 종합
            analysis_result = {
                "file_name": file_name,
                "novel_name": novel_name,
                "content_analysis": content_analysis,
                "conflicts": conflicts,
                "recommendations": recommendations,
                "summary": self._generate_summary(content_analysis, conflicts, recommendations)
            }
            
            return analysis_result
            
        except Exception as e:
            return {
                "error": f"분석 중 오류가 발생했습니다: {str(e)}",
                "file_name": file_name,
                "novel_name": novel_name
            }
    
    def _check_conflicts(self, novel_name: str, content_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        기존 데이터베이스와의 충돌을 확인
        
        Args:
            novel_name: 소설 이름
            content_analysis: 내용 분석 결과
            
        Returns:
            충돌 정보 딕셔너리
        """
        conflicts = {
            "character_conflicts": [],
            "world_setting_conflicts": [],
            "timeline_conflicts": []
        }
        
        # 인물 충돌 확인
        existing_characters = self.db_manager.get_characters(novel_name)
        new_characters = content_analysis.get("characters", [])
        
        for new_char in new_characters:
            for existing_char in existing_characters:
                if self._is_character_conflict(new_char, existing_char):
                    conflicts["character_conflicts"].append({
                        "new_character": new_char,
                        "existing_character": existing_char,
                        "conflict_type": "character_overlap"
                    })
        
        # 세계관 설정 충돌 확인
        existing_world_settings = self.db_manager.get_world_settings(novel_name)
        new_world_elements = content_analysis.get("world_elements", [])
        
        for new_element in new_world_elements:
            for existing_element in existing_world_settings:
                if self._is_world_setting_conflict(new_element, existing_element):
                    conflicts["world_setting_conflicts"].append({
                        "new_element": new_element,
                        "existing_element": existing_element,
                        "conflict_type": "world_setting_conflict"
                    })
        
        # 타임라인 충돌 확인
        existing_timeline = self.db_manager.get_timeline_events(novel_name)
        new_events = content_analysis.get("events", [])
        
        for new_event in new_events:
            for existing_event in existing_timeline:
                if self._is_timeline_conflict(new_event, existing_event):
                    conflicts["timeline_conflicts"].append({
                        "new_event": new_event,
                        "existing_event": existing_event,
                        "conflict_type": "timeline_conflict"
                    })
        
        return conflicts
    
    def _generate_recommendations(self, novel_name: str, content_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        새로운 내용에 대한 추천 옵션 생성
        
        Args:
            novel_name: 소설 이름
            content_analysis: 내용 분석 결과
            
        Returns:
            추천 옵션 딕셔너리
        """
        recommendations = {
            "storyboard_suggestions": [],
            "character_suggestions": [],
            "world_setting_suggestions": [],
            "timeline_suggestions": []
        }
        
        # 스토리보드 추천
        storyboard_suggestions = self.recommendation_engine.generate_storyboard_suggestions(
            content_analysis, novel_name
        )
        recommendations["storyboard_suggestions"] = storyboard_suggestions
        
        # 인물 추천
        character_suggestions = self.recommendation_engine.generate_character_suggestions(
            content_analysis, novel_name
        )
        recommendations["character_suggestions"] = character_suggestions
        
        # 세계관 설정 추천
        world_setting_suggestions = self.recommendation_engine.generate_world_setting_suggestions(
            content_analysis, novel_name
        )
        recommendations["world_setting_suggestions"] = world_setting_suggestions
        
        # 타임라인 추천
        timeline_suggestions = self.recommendation_engine.generate_timeline_suggestions(
            content_analysis, novel_name
        )
        recommendations["timeline_suggestions"] = timeline_suggestions
        
        return recommendations
    
    def _is_character_conflict(self, new_char: Dict[str, Any], existing_char: Dict[str, Any]) -> bool:
        """인물 충돌 여부 확인"""
        # 이름이 같거나 유사한 경우
        if new_char.get("name", "").lower() == existing_char.get("name", "").lower():
            return True
        
        # 역할이나 특징이 충돌하는 경우
        new_role = new_char.get("role", "")
        existing_role = existing_char.get("role", "")
        
        if new_role and existing_role and new_role == existing_role:
            return True
        
        return False
    
    def _is_world_setting_conflict(self, new_element: Dict[str, Any], existing_element: Dict[str, Any]) -> bool:
        """세계관 설정 충돌 여부 확인"""
        # 설정 이름이 같거나 유사한 경우
        if new_element.get("name", "").lower() == existing_element.get("name", "").lower():
            return True
        
        # 설정 내용이 충돌하는 경우
        new_description = new_element.get("description", "")
        existing_description = existing_element.get("description", "")
        
        # 간단한 키워드 기반 충돌 확인
        new_keywords = set(new_description.lower().split())
        existing_keywords = set(existing_description.lower().split())
        
        if len(new_keywords.intersection(existing_keywords)) > 3:  # 3개 이상 키워드가 겹치면 충돌로 간주
            return True
        
        return False
    
    def _is_timeline_conflict(self, new_event: Dict[str, Any], existing_event: Dict[str, Any]) -> bool:
        """타임라인 충돌 여부 확인"""
        # 날짜가 같은 경우
        new_date = new_event.get("date", "")
        existing_date = existing_event.get("date", "")
        
        if new_date and existing_date and new_date == existing_date:
            return True
        
        # 이벤트 내용이 유사한 경우
        new_description = new_event.get("description", "")
        existing_description = existing_event.get("description", "")
        
        if new_description and existing_description:
            # 간단한 유사도 확인
            new_words = set(new_description.lower().split())
            existing_words = set(existing_description.lower().split())
            
            if len(new_words.intersection(existing_words)) > 5:  # 5개 이상 단어가 겹치면 충돌로 간주
                return True
        
        return False
    
    def _generate_summary(self, content_analysis: Dict[str, Any], conflicts: Dict[str, Any], recommendations: Dict[str, Any]) -> str:
        """분석 결과 요약 생성"""
        summary_parts = []
        
        # 내용 분석 요약
        characters_count = len(content_analysis.get("characters", []))
        world_elements_count = len(content_analysis.get("world_elements", []))
        events_count = len(content_analysis.get("events", []))
        
        summary_parts.append(f"분석된 내용: 인물 {characters_count}명, 세계관 요소 {world_elements_count}개, 이벤트 {events_count}개")
        
        # 충돌 요약
        total_conflicts = (
            len(conflicts.get("character_conflicts", [])) +
            len(conflicts.get("world_setting_conflicts", [])) +
            len(conflicts.get("timeline_conflicts", []))
        )
        
        if total_conflicts > 0:
            summary_parts.append(f"발견된 충돌: {total_conflicts}개")
        else:
            summary_parts.append("충돌 없음")
        
        # 추천 요약
        total_recommendations = (
            len(recommendations.get("storyboard_suggestions", [])) +
            len(recommendations.get("character_suggestions", [])) +
            len(recommendations.get("world_setting_suggestions", [])) +
            len(recommendations.get("timeline_suggestions", []))
        )
        
        summary_parts.append(f"추천 사항: {total_recommendations}개")
        
        return " | ".join(summary_parts)
    
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
        report_parts.append(f"# 📊 파일 분석 결과: {analysis_result['file_name']}")
        report_parts.append("")
        
        # 요약
        report_parts.append(f"## 📋 요약")
        report_parts.append(analysis_result['summary'])
        report_parts.append("")
        
        # 충돌 정보
        conflicts = analysis_result.get('conflicts', {})
        if any(conflicts.values()):
            report_parts.append("## ⚠️ 발견된 충돌")
            
            if conflicts.get('character_conflicts'):
                report_parts.append("### 인물 충돌")
                for conflict in conflicts['character_conflicts']:
                    report_parts.append(f"- **{conflict['new_character'].get('name', 'Unknown')}** ↔️ **{conflict['existing_character'].get('name', 'Unknown')}**")
                report_parts.append("")
            
            if conflicts.get('world_setting_conflicts'):
                report_parts.append("### 세계관 설정 충돌")
                for conflict in conflicts['world_setting_conflicts']:
                    report_parts.append(f"- **{conflict['new_element'].get('name', 'Unknown')}** ↔️ **{conflict['existing_element'].get('name', 'Unknown')}**")
                report_parts.append("")
            
            if conflicts.get('timeline_conflicts'):
                report_parts.append("### 타임라인 충돌")
                for conflict in conflicts['timeline_conflicts']:
                    report_parts.append(f"- **{conflict['new_event'].get('date', 'Unknown')}** ↔️ **{conflict['existing_event'].get('date', 'Unknown')}**")
                report_parts.append("")
        else:
            report_parts.append("## ✅ 충돌 없음")
            report_parts.append("새로 추가된 내용과 기존 설정 간 충돌이 발견되지 않았습니다.")
            report_parts.append("")
        
        # 추천 사항
        recommendations = analysis_result.get('recommendations', {})
        if any(recommendations.values()):
            report_parts.append("## 💡 추천 사항")
            
            if recommendations.get('storyboard_suggestions'):
                report_parts.append("### 스토리보드 추천")
                for suggestion in recommendations['storyboard_suggestions']:
                    report_parts.append(f"- {suggestion}")
                report_parts.append("")
            
            if recommendations.get('character_suggestions'):
                report_parts.append("### 인물 설정 추천")
                for suggestion in recommendations['character_suggestions']:
                    report_parts.append(f"- {suggestion}")
                report_parts.append("")
            
            if recommendations.get('world_setting_suggestions'):
                report_parts.append("### 세계관 설정 추천")
                for suggestion in recommendations['world_setting_suggestions']:
                    report_parts.append(f"- {suggestion}")
                report_parts.append("")
            
            if recommendations.get('timeline_suggestions'):
                report_parts.append("### 타임라인 추천")
                for suggestion in recommendations['timeline_suggestions']:
                    report_parts.append(f"- {suggestion}")
                report_parts.append("")
        
        return "\n".join(report_parts)

    def extract_recommendations(self, analysis_result, db_data):
        """
        분석 결과와 DB(스토리보드/인물)를 비교하여 추천 항목을 추출합니다.
        반환 예시:
        {
            "character_recommendations": {
                "add": [ ... ],
                "update": [ ... ]
            },
            "storyboard_recommendations": {
                "add": [ ... ],
                "update": [ ... ]
            }
        }
        """
        recommendations = {
            "character_recommendations": {"add": [], "update": []},
            "storyboard_recommendations": {"add": [], "update": []}
        }

        # 인물 비교
        db_characters = {c.get("name"): c for c in db_data.get("characters", [])}
        for char in analysis_result.get("characters", []):
            name = char.get("name")
            if not name:
                continue
            if name not in db_characters:
                recommendations["character_recommendations"]["add"].append({
                    "name": name,
                    "reason": "DB에 없는 신규 인물",
                    "data": char
                })
            else:
                # 주요 속성 비교(성격, 배경 등)
                db_char = db_characters[name]
                diff = {}
                for k in ["role", "personality", "background"]:
                    if char.get(k) != db_char.get(k):
                        diff[k] = {"old": db_char.get(k), "new": char.get(k)}
                if diff:
                    rec = {
                        "name": name,
                        "reason": f"속성 불일치: {', '.join(diff.keys())}",
                        "data": char,
                        "diff": diff
                    }
                    recommendations["character_recommendations"]["update"].append(rec)

        # 스토리보드(씬) 비교
        db_scenes = {s.get("title"): s for s in db_data.get("storyboards", [])}
        for scene in analysis_result.get("events", []):
            title = scene.get("title")
            if not title:
                continue
            if title not in db_scenes:
                recommendations["storyboard_recommendations"]["add"].append({
                    "target": "scene",
                    "name": title,
                    "reason": "DB에 없는 신규 씬",
                    "data": scene
                })
            else:
                db_scene = db_scenes[title]
                diff = {}
                for k in ["description", "date", "importance"]:
                    if scene.get(k) != db_scene.get(k):
                        diff[k] = {"old": db_scene.get(k), "new": scene.get(k)}
                if diff:
                    rec = {
                        "target": "scene",
                        "name": title,
                        "reason": f"속성 불일치: {', '.join(diff.keys())}",
                        "data": scene,
                        "diff": diff
                    }
                    recommendations["storyboard_recommendations"]["update"].append(rec)

        return recommendations

    def apply_recommendation(self, rec, db_path):
        """
        추천 항목(rec)을 DB에 반영합니다.
        - rec: 추천 항목(dict)
        - db_path: 적용할 DB 파일 경로(폴더)
        """
        from pathlib import Path
        import json

        # 인물
        if rec.get("name") and rec.get("data"):
            char_dir = Path(db_path) / "characters"
            char_dir.mkdir(parents=True, exist_ok=True)
            file_path = char_dir / f"character_{rec['name']}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(rec["data"], f, ensure_ascii=False, indent=2)
            return True

        # 씬(스토리보드)
        if rec.get("target") == "scene" and rec.get("data"):
            sb_dir = Path(db_path) / "Storyboard"
            sb_dir.mkdir(parents=True, exist_ok=True)
            file_path = sb_dir / f"storyboard_{rec['name']}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(rec["data"], f, ensure_ascii=False, indent=2)
            return True

        return False 