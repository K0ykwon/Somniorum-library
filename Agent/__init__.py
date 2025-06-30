"""
AI 분석 에이전트 패키지

이 패키지는 소설 파일 추가 시 AI 분석을 수행하는 기능을 제공합니다.
"""

from .Agent import NovelAnalysisAgent
from .openai_agent import OpenAINovelAnalysisAgent
from .utils import DatabaseManager, ContentAnalyzer, RecommendationEngine
from .config import AgentConfig

__version__ = "1.0.0"
__author__ = "Somniorum Library"

__all__ = [
    "NovelAnalysisAgent",
    "OpenAINovelAnalysisAgent",
    "DatabaseManager", 
    "ContentAnalyzer",
    "RecommendationEngine",
    "AgentConfig"
] 