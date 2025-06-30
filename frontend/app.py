import streamlit as st
from streamlit_option_menu import option_menu
import streamlit.components.v1 as components
import os
from pathlib import Path
import plotly.graph_objects as go
import sys
from dotenv import load_dotenv
import datetime
import json

# .env 파일 로드
load_dotenv()

# Agent 모듈 import (test_simple.py와 동일한 방식)
sys.path.append(str(Path(__file__).parent.parent))
from Agent import OpenAINovelAnalysisAgent

# --- 사용자 정의 스타일 ---
st.markdown(
    """
    <style>
    html, body, main, [data-testid="stAppViewContainer"] {
        overflow: hidden !important;
        height: 100vh !important;
    }
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100vw;
    }

    /* 중앙 편집기 스타일 */
    div[data-testid="column"]:nth-of-type(2) > div {
        min-height: 92vh !important;
        padding: 2.5rem 1.5rem 2rem 1.5rem;
        margin-bottom: 1rem !important;
        background: #ffffff;
        display: flex;
        flex-direction: column;
        justify-content: stretch;
        margin-top: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
    }

    /* 우측 AI 대화 영역 - 고정 위치 */
    div[data-testid="column"]:nth-of-type(3) > div {
        position: fixed !important;
        right: 0 !important;
        top: 0 !important;
        width: 33% !important;
        height: 100vh !important;
        background: #e3e6ea;
        border-left: 4px solid #b0b0b0;
        box-shadow: -6px 0 24px rgba(0, 0, 0, 0.15);
        padding: 2.5rem 1.5rem 2rem 2rem;
        margin-bottom: 1rem !important;
        border-radius: 20px 0 0 20px;
        display: flex;
        flex-direction: column;
        margin-top: 1.5rem;
        z-index: 1000 !important;
    }

    /* AI 대화 헤더 크기 및 여백 조정 */
    div[data-testid="column"]:nth-of-type(3) h1 {
        font-size: 1.5rem !important;
        margin-top: 1.5rem !important;
        margin-bottom: 1.2rem !important;
    }

    /* columns 간 간격 최소화 */
    section[data-testid="stHorizontalBlock"] > div {
        gap: 0.25rem !important;
    }

    /* 하위 메뉴 스타일 */
    .novel-submenu {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        margin-top: 1rem;
    }
    .novel-submenu-btn {
        background: #f5f5f5;
        border: none;
        border-radius: 8px;
        padding: 0.7rem 1rem;
        font-size: 1rem;
        text-align: left;
        cursor: pointer;
        transition: background 0.2s;
    }
    .novel-submenu-btn.selected {
        background: #e0e6f7;
        font-weight: bold;
        color: #2a3b8f;
    }
    .novel-submenu-btn:hover {
        background: #e9e9e9;
    }
    /* option_menu active-indicator(파란색) 제거 */
    .nav-pills .nav-link.active, .nav-pills .show > .nav-link {
        background-color: transparent !important;
        color: inherit !important;
        border: none !important;
        box-shadow: none !important;
    }
    .nav-pills .nav-link {
        border: none !important;
    }
    .nav-pills .nav-link:after {
        display: none !important;
    }
    
    /* 톱니바퀴 버튼 스타일 */
    button[data-testid="baseButton-secondary"] {
        font-size: 1.5rem !important;
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0.5rem !important;
        margin-left: 0.5rem !important;
        display: inline-block !important;
        vertical-align: middle !important;
    }
    button[data-testid="baseButton-secondary"]:hover {
        background: rgba(0,0,0,0.05) !important;
        border-radius: 50% !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 컬럼 비율 조정: 세로선 column 제거 ---
left_col, center_col, right_col = st.columns([0.5, 7, 4.5], gap="small")

# --- 상태 관리: 선택된 소설/하위 항목 ---
if 'selected_novel' not in st.session_state:
    st.session_state['selected_novel'] = ''
if 'selected_novel_tab' not in st.session_state:
    st.session_state['selected_novel_tab'] = '소설파일'
# AI 분석 로그 저장소 추가
if 'ai_analysis_logs' not in st.session_state:
    st.session_state['ai_analysis_logs'] = []
if 'show_analysis_logs' not in st.session_state:
    st.session_state['show_analysis_logs'] = False

# --- 좌측 사이드바 (Streamlit Sidebar 사용) ---
with st.sidebar:
    st.header('소설 관리')
    # Database 폴더에서 소설 목록 불러오기
    db_dir = Path('Database')
    db_dir.mkdir(exist_ok=True)
    novel_dirs = [d.name for d in db_dir.iterdir() if d.is_dir()]
    if 'novels' not in st.session_state:
        st.session_state['novels'] = novel_dirs
    else:
        # 파일 시스템과 동기화
        st.session_state['novels'] = novel_dirs
    sidebar_options = ["소설 추가"]
    sidebar_icons = ["plus-circle"]
    if st.session_state['novels']:
        sidebar_options.append("소설 목록")
        sidebar_icons.append("list-task")
    selected = option_menu(
        menu_title=None,
        options=sidebar_options,
        icons=sidebar_icons,
        menu_icon="cast",
        default_index=0,
    )
    if selected == "소설 추가":
        st.subheader('새 소설 추가')
        novel_name = st.text_input('소설 이름', key='novel_name_input')
        if st.button('추가', key='add_novel_btn'):
            if novel_name and novel_name not in st.session_state['novels']:
                # Database/[소설이름]/Storyboard, characters, Timeline 생성
                base_path = db_dir / novel_name
                (base_path / 'Files').mkdir(parents=True, exist_ok=True)
                (base_path / 'Storyboard').mkdir(parents=True, exist_ok=True)
                (base_path / 'characters').mkdir(parents=True, exist_ok=True)
                (base_path / 'Timeline').mkdir(parents=True, exist_ok=True)
                st.success(f'"{novel_name}" 소설이 추가되었습니다.')
                st.rerun()
    elif selected == "소설 목록":
        if st.session_state['novels']:
            novel = st.selectbox('소설 선택', st.session_state['novels'], key='novel_select')
            st.session_state['selected_novel'] = novel
            st.markdown(f'### "{novel}" 관리')
            # 하위 메뉴(버튼)
            submenu_items = ["소설파일", "소설 스토리보드", "인물", "세계관", "타임라인"]
            st.markdown('<div class="novel-submenu">', unsafe_allow_html=True)
            for item in submenu_items:
                selected_class = 'selected' if st.session_state['selected_novel_tab'] == item else ''
                if st.button(item, key=f"submenu_{item}", help=item, use_container_width=True):
                    st.session_state['selected_novel_tab'] = item
                    # 새 탭으로 넘어갈 때 AI 분석 결과 자동으로 닫기
                    st.session_state['show_analysis_result'] = False
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            # --- 구분선 및 AI 분석 로그 버튼 추가 ---
            st.markdown('---')
            if st.button('📋 AI 분석 로그 보기', key='sidebar_show_analysis_logs', use_container_width=True):
                st.session_state['show_analysis_logs'] = not st.session_state.get('show_analysis_logs', False)
                st.session_state['show_analysis_logs_from_sidebar'] = True
                st.rerun()
        else:
            st.session_state['selected_novel'] = ''
            st.session_state['selected_novel_tab'] = '소설파일'

# --- 중앙: AI 분석 로그 표시 (사이드바 버튼 클릭 시) ---
with center_col:
    if st.session_state.get('show_analysis_logs', False) and st.session_state.get('show_analysis_logs_from_sidebar', False):
        current_novel = st.session_state.get('selected_novel', '')
        st.markdown(f"## 📋 '{current_novel}' AI 분석 로그")
        logs = [log for log in st.session_state.get('ai_analysis_logs', []) if log.get('novel') == current_novel]
        if logs:
            recent_logs = logs[-10:]
            for idx, log in enumerate(reversed(recent_logs)):
                status_color = "🟢" if log.get('status') == '분석 완료' else "🟡"
                st.markdown(f"{status_color} **{log['timestamp']}** - {log['file']}")
                st.markdown(f"   - 액션: {log['action']} | 상태: {log['status']}")
                if 'result_count' in log:
                    st.markdown(f"   - 분석 결과: {log['result_count']}개 항목")
                # 분석 결과 expander - 모든 내용 표시
                if log.get('analysis_result'):
                    with st.expander('🔍 분석 결과 상세 보기', expanded=False):
                        # 요약
                        summary = log.get('summary', '')
                        if summary:
                            st.info(summary)
                        
                        # 인물 분석
                        characters = log.get('characters', [])
                        if characters:
                            st.markdown("### 👥 발견된 인물")
                            for char in characters:
                                st.markdown(f"- **{char.get('name', 'Unknown')}** ({char.get('role', '미정')})")
                                if char.get('personality'):
                                    st.markdown(f"  - 성격: {char['personality']}")
                                if char.get('background'):
                                    st.markdown(f"  - 배경: {char['background']}")
                        
                        # 세계관 요소
                        world_elements = log.get('world_elements', [])
                        if world_elements:
                            st.markdown("### 🌍 세계관 요소")
                            for element in world_elements:
                                st.markdown(f"- **{element.get('name', 'Unknown')}** ({element.get('category', '기타')})")
                                if element.get('description'):
                                    st.markdown(f"  - {element['description']}")
                        
                        # 이벤트
                        events = log.get('events', [])
                        if events:
                            st.markdown("### 📅 발견된 이벤트")
                            for event in events:
                                st.markdown(f"- **{event.get('title', 'Unknown')}** ({event.get('date', '날짜 미정')})")
                                st.markdown(f"  - 중요도: {event.get('importance', '보통')}")
                                if event.get('description'):
                                    st.markdown(f"  - {event['description']}")
                        
                        # 스토리 구조
                        story_structure = log.get('story_structure', {})
                        if story_structure:
                            st.markdown("### 📖 스토리 구조")
                            if story_structure.get('conflict'):
                                st.markdown(f"- 갈등: {story_structure['conflict']}")
                            if story_structure.get('resolution'):
                                st.markdown(f"- 해결: {story_structure['resolution']}")
                            if story_structure.get('pacing'):
                                st.markdown(f"- 전개 속도: {story_structure['pacing']}")
                        
                        # 모순 분석 결과
                        conflicts = log.get('conflicts', {})
                        # 실제 모순만 체크 (새로운 정보는 문제가 아님)
                        has_contradictions = (
                            conflicts.get('internal_contradictions') or 
                            conflicts.get('external_contradictions')
                        )
                        if has_contradictions:
                            print(conflicts.values())
                            st.markdown("### 🔍 충돌 분석")
                            
                            # 심각도별 색상 매핑
                            severity_colors = {
                                "심각": "🔴",
                                "보통": "🟡", 
                                "경미": "🟢"
                            }
                            
                            # 내부 모순 표시
                            if 'internal_contradictions' in conflicts and conflicts['internal_contradictions']:
                                st.markdown("#### 📖 내부 모순 (소설 내용 내)")
                                for i, contradiction in enumerate(conflicts['internal_contradictions']):
                                    severity_icon = severity_colors.get(contradiction.get('severity', '보통'), '🟡')
                                    st.markdown(f"**{severity_icon} {contradiction.get('type', '모순')} - {contradiction.get('description', '')[:50]}...**")
                                    st.markdown(f"- 유형: {contradiction.get('type', '')}")
                                    st.markdown(f"- 설명: {contradiction.get('description', '')}")
                                    st.markdown(f"- 심각도: {severity_icon} {contradiction.get('severity', '')}")
                                    if contradiction.get('elements'):
                                        st.markdown("- 모순되는 요소:")
                                        for element in contradiction['elements']:
                                            st.markdown(f"    - {element}")
                                    if contradiction.get('suggestion'):
                                        st.markdown(f"- 해결 방안: {contradiction['suggestion']}")
                            
                            # 외부 모순 표시
                            if 'external_contradictions' in conflicts and conflicts['external_contradictions']:
                                st.markdown("#### 🗄️ 외부 모순 (기존 설정과)")
                                for i, contradiction in enumerate(conflicts['external_contradictions']):
                                    severity_icon = severity_colors.get(contradiction.get('severity', '보통'), '🟡')
                                    st.markdown(f"**{severity_icon} {contradiction.get('type', '모순')} - {contradiction.get('description', '')[:50]}...**")
                                    st.markdown(f"- 유형: {contradiction.get('type', '')}")
                                    st.markdown(f"- 설명: {contradiction.get('description', '')}")
                                    st.markdown(f"- 심각도: {severity_icon} {contradiction.get('severity', '')}")
                                    if contradiction.get('new_element'):
                                        st.markdown(f"- 새로운 내용: {contradiction['new_element']}")
                                    if contradiction.get('existing_element'):
                                        st.markdown(f"- 기존 설정: {contradiction['existing_element']}")
                                    if contradiction.get('suggestion'):
                                        st.markdown(f"- 해결 방안: {contradiction['suggestion']}")
                            
                            # 기존 충돌 분석 결과 표시 (하위 호환성)
                            if 'character_conflicts' in conflicts and conflicts['character_conflicts']:
                                st.markdown("#### ⚠️ 기존 충돌 분석 (하위 호환)")
                                for conflict in conflicts['character_conflicts']:
                                    st.warning(f"**인물 충돌:** {conflict.get('new_character', '')} vs {conflict.get('existing_character', '')} - {conflict.get('description', '')}")
                            
                            if 'world_setting_conflicts' in conflicts and conflicts['world_setting_conflicts']:
                                for conflict in conflicts['world_setting_conflicts']:
                                    st.warning(f"**세계관 충돌:** {conflict.get('new_element', '')} vs {conflict.get('existing_element', '')} - {conflict.get('description', '')}")
                            
                            if 'timeline_conflicts' in conflicts and conflicts['timeline_conflicts']:
                                for conflict in conflicts['timeline_conflicts']:
                                    st.warning(f"**타임라인 충돌:** {conflict.get('new_event', '')} vs {conflict.get('existing_event', '')} - {conflict.get('description', '')}")
                        else:
                            st.markdown("### 🔍 충돌 분석")
                            st.info("✅ 모순 없음 - 내용상 모순이 발견되지 않았습니다.")
                        
                        # 추천 사항
                        recommendations = log.get('recommendations', {})
                        if any(recommendations.values()):
                            st.markdown("### 💡 AI 추천 사항")
                            if recommendations.get('storyboard_suggestions'):
                                st.markdown("**📝 스토리보드 발전 방향:**")
                                for suggestion in recommendations['storyboard_suggestions']:
                                    st.markdown(f"- {suggestion}")
                            if recommendations.get('character_suggestions'):
                                st.markdown("**👤 인물 설정 보완:**")
                                for suggestion in recommendations['character_suggestions']:
                                    st.markdown(f"- {suggestion}")
                            if recommendations.get('world_setting_suggestions'):
                                st.markdown("**🌍 세계관 설정 확장:**")
                                for suggestion in recommendations['world_setting_suggestions']:
                                    st.markdown(f"- {suggestion}")
                            if recommendations.get('timeline_suggestions'):
                                st.markdown("**📅 타임라인 구성 개선:**")
                                for suggestion in recommendations['timeline_suggestions']:
                                    st.markdown(f"- {suggestion}")
                        
                        # 전체 텍스트 리포트
                        if log.get('analysis_report'):
                            st.markdown("---")
                            st.markdown("### 📋 전체 분석 리포트")
                            st.markdown(log['analysis_report'])
                        # --- 정보 추출 버튼 추가 (로그 상세 내) ---
                        if st.button('정보 추출', key=f'extract_info_btn_log_{idx}', use_container_width=True):
                            st.session_state['info_extract_clicked'] = True
                            st.rerun()
        else:
            # 로그가 없을 때 메시지 표시
            st.info("아직 AI 분석 로그가 없습니다.")
        
        # 로그 닫기 버튼 (로그가 있든 없든 항상 표시)
        if st.button("로그 닫기", key="close_logs_btn_center", use_container_width=True):
            st.session_state['show_analysis_logs'] = False
            st.session_state['show_analysis_logs_from_sidebar'] = False
            st.rerun()
        
        st.markdown("---")

# --- 중앙: 편집기 영역 ---
with center_col:
    novel_title = st.session_state.get('selected_novel', '')
    st.header(novel_title if novel_title else '')
    
    tab = st.session_state.get('selected_novel_tab', '소설파일')

    # 탭이 바뀔 때마다 info_extract_clicked 초기화
    if 'last_tab' not in st.session_state or st.session_state['last_tab'] != tab:
        st.session_state['info_extract_clicked'] = False
        st.session_state['last_tab'] = tab

    def sync_novel_files(novel_name):
        file_dir = db_dir / novel_name / 'Files'
        files = []
        if file_dir.exists():
            for file in file_dir.glob('*'):
                if file.is_file():
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        files.append({'title': file.name, 'content': content})
                    except Exception as e:
                        pass  # 파일 읽기 실패 시 무시
        st.session_state['novel_files'][novel_name] = files

    if tab == '소설파일':
        # 소설별 파일 리스트 관리 (제목+내용 딕셔너리)
        if 'novel_files' not in st.session_state:
            st.session_state['novel_files'] = {}
        current_novel = st.session_state.get('selected_novel', '')
        if current_novel and current_novel not in st.session_state['novel_files']:
            st.session_state['novel_files'][current_novel] = []
        # show_file_tabs 초기화(처음엔 False)
        if 'show_file_tabs' not in st.session_state:
            st.session_state['show_file_tabs'] = False
        show_tabs = st.session_state.get('show_file_tabs', False)
        selected_file_idx = st.session_state.get('selected_file_idx', None)
        # 파일 추가 입력 위젯의 고유 키(매번 새로 생성)
        if 'file_input_key' not in st.session_state:
            st.session_state['file_input_key'] = 0

        # 파일 수정 폼 표시 상태 관리
        if 'show_edit_form' not in st.session_state:
            st.session_state['show_edit_form'] = False

        # 소설 선택 시 항상 파일 목록 동기화
        if current_novel:
            sync_novel_files(current_novel)

        # 소설이 선택된 경우에만 파일 관련 UI 표시
        if current_novel:
            st.subheader('파일 목록')
            files = st.session_state['novel_files'].get(current_novel, [])
            file_titles = [file['title'] for file in files]
            selected_file_idx = None
            # 드롭다운에서 파일 선택 시 on_change 콜백으로만 상태 갱신
            def on_selectbox_change():
                st.session_state['selected_file_idx'] = st.session_state[f'selectbox_idx_{current_novel}_{st.session_state.get("selectbox_key_counter", 0)}']
                st.session_state['show_file_tabs'] = False
                st.session_state['show_edit_form'] = False
                st.session_state['show_view_file'] = False
            if file_titles:
                if f'selectbox_idx_{current_novel}' not in st.session_state:
                    st.session_state[f'selectbox_idx_{current_novel}'] = 0
                
                # 파일 목록이 변경되었을 때 인덱스 조정
                current_file_count = len(file_titles)
                if st.session_state[f'selectbox_idx_{current_novel}'] >= current_file_count:
                    st.session_state[f'selectbox_idx_{current_novel}'] = 0
                
                selected_idx = st.selectbox(
                    '파일 선택',
                    range(len(file_titles)),
                    format_func=lambda i: file_titles[i],
                    key=f'selectbox_idx_{current_novel}_{st.session_state.get("selectbox_key_counter", 0)}',
                    on_change=on_selectbox_change
                )
                selected_file_idx = st.session_state.get('selected_file_idx', selected_idx)
                # selected_file_idx가 None이면 selected_idx 사용
                if selected_file_idx is None:
                    selected_file_idx = selected_idx
                # selected_file_idx가 유효하지 않으면 selected_idx 사용
                if selected_file_idx >= len(files):
                    selected_file_idx = selected_idx
                # 파일 열람/추가/수정/삭제 버튼을 한 줄에 배치 (2:1:1:1 비율, 간격 좁게)
                btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1,1,1,1], gap="small")
                with btn_col1:
                    if st.button('파일 열람', key=f'view_file_btn_{current_novel}', use_container_width=True):
                        st.session_state['show_file_tabs'] = False
                        st.session_state['show_edit_form'] = False
                        st.session_state['show_view_file'] = True
                        st.rerun()
                with btn_col2:
                    if st.button('파일 추가', key=f'add_file_btn_{current_novel}', use_container_width=True):
                        st.session_state['show_file_tabs'] = True
                        st.session_state['show_edit_form'] = False
                        st.session_state['show_view_file'] = False
                        st.rerun()
                with btn_col3:
                    if st.button('파일 수정', key=f'edit_file_btn_{current_novel}', use_container_width=True):
                        st.session_state['show_edit_form'] = True
                        st.session_state['show_file_tabs'] = False
                        st.session_state['show_view_file'] = False
                        st.rerun()
                with btn_col4:
                    if st.button('파일 삭제', key=f'delete_file_btn_{current_novel}', use_container_width=True):
                        if selected_file_idx is not None and 0 <= selected_file_idx < len(files):
                            # 파일 삭제 상태 설정
                            st.session_state['show_delete_confirm'] = True
                            st.session_state['file_to_delete'] = files[selected_file_idx]['title']
                            st.rerun()
            else:
                st.session_state['selected_file_idx'] = None
                st.session_state['show_edit_form'] = False
                st.session_state['show_view_file'] = False
                # 파일이 없으면 파일 추가 버튼만 꽉 채워서 표시
                btn_col = st.columns(1)
                with btn_col[0]:
                    st.markdown('---')
                    if st.button('파일 추가', key=f'add_file_btn_{current_novel}', use_container_width=True):
                        st.session_state['show_file_tabs'] = True
                        st.session_state['show_edit_form'] = False
                        st.session_state['show_view_file'] = False
                        st.rerun()

            # 삭제 확인 UI
            if st.session_state.get('show_delete_confirm', False):
                file_to_delete = st.session_state.get('file_to_delete', '')
                st.warning(f'"{file_to_delete}" 파일을 삭제하시겠습니까?')
                
                if st.button('삭제 확인', key=f'confirm_delete_{current_novel}'):
                    # 파일 시스템에서 삭제
                    file_save_dir = db_dir / current_novel / 'Files'
                    file_path = file_save_dir / file_to_delete
                    if file_path.exists():
                        file_path.unlink()
                    sync_novel_files(current_novel)
                    st.success(f'"{file_to_delete}" 파일이 삭제되었습니다.')
                    
                    # 인덱스 초기화 (selectbox 키는 직접 수정하지 않음)
                    st.session_state['selected_file_idx'] = 0
                    st.session_state['show_delete_confirm'] = False
                    st.session_state['file_to_delete'] = ''
                    st.session_state['show_edit_form'] = False
                    st.session_state['show_view_file'] = False
                    # selectbox 키 카운터 증가하여 새로운 위젯 생성
                    st.session_state['selectbox_key_counter'] = st.session_state.get('selectbox_key_counter', 0) + 1
                    
                    # 페이지 리로드
                    st.rerun()
                
                if st.button('취소', key=f'cancel_delete_{current_novel}'):
                    st.session_state['show_delete_confirm'] = False
                    st.session_state['file_to_delete'] = ''
                    st.rerun()

            # 파일 추가/작성/업로드 탭
            if show_tabs:
                st.markdown('---')
                st.subheader('파일 추가')
                tab_mode = st.radio('', ['파일 업로드', '파일 작성'], horizontal=True, key=f'file_tab_mode_{current_novel}', label_visibility='collapsed')
                if tab_mode == '파일 업로드':
                    uploaded_file = st.file_uploader('파일 업로드', type=['txt', 'md'], key=f'file_uploader_{current_novel}_{st.session_state["file_input_key"]}')
                    if uploaded_file is not None and current_novel:
                        # 파일 내용 읽기
                        content = uploaded_file.read().decode('utf-8')
                        
                        # 파일명 표시 (수정 가능)
                        file_name = st.text_input('파일명', value=uploaded_file.name, key=f'upload_file_name_{current_novel}_{st.session_state["file_input_key"]}')
                        
                        # 파일 내용 표시 (수정 가능)
                        st.markdown('**파일 내용 (수정 가능):**')
                        modified_content = st.text_area('내용', value=content, height=300, key=f'upload_file_content_{current_novel}_{st.session_state["file_input_key"]}')
                        
                        # 저장 버튼
                        if st.button('파일 저장', key=f'confirm_file_upload_{current_novel}_{st.session_state["file_input_key"]}'):
                            if file_name.strip() and current_novel:
                                # 파일을 Database/[소설이름]/Files/에 저장
                                file_save_dir = db_dir / current_novel / 'Files'
                                file_save_dir.mkdir(parents=True, exist_ok=True)
                                file_path = file_save_dir / file_name
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.write(modified_content)
                                
                                # AI 분석 수행
                                
                                st.success(f'"{file_name}" 파일이 추가 및 저장되었습니다.')
                                
                                sync_novel_files(current_novel)
                                st.session_state['show_file_tabs'] = False
                                st.session_state['file_input_key'] += 1
                                st.session_state['show_edit_form'] = False
                                st.session_state['selected_file_idx'] = 0
                                st.session_state['selectbox_key_counter'] = st.session_state.get('selectbox_key_counter', 0) + 1
                                st.rerun()  # 분석 결과 표시를 위해 페이지 새로고침
                            else:
                                st.warning('파일명을 입력해주세요.')
                elif tab_mode == '파일 작성':
                    file_title = st.text_input('제목', value='', key=f'file_title_input_{current_novel}_{st.session_state["file_input_key"]}')
                    file_content = st.text_area('내용', value='', key=f'file_content_input_{current_novel}_{st.session_state["file_input_key"]}', height=200)
                    if st.button('확인', key=f'confirm_file_write_{current_novel}_{st.session_state["file_input_key"]}'):
                        if file_title.strip() and current_novel:
                            file_save_dir = db_dir / current_novel / 'Files'
                            file_save_dir.mkdir(parents=True, exist_ok=True)
                            file_path = file_save_dir / file_title
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(file_content)
                            
                            # AI 분석 수행
                            st.write("🔍 AI 분석 시작...")
                            agent = OpenAINovelAnalysisAgent()
                            st.write("✅ Agent 초기화 완료")
                            
                            # AI 분석 로그 저장
                            log_entry = {
                                'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'novel': current_novel,
                                'file': file_title,
                                'action': '파일 작성',
                                'status': '분석 시작'
                            }
                            st.session_state['ai_analysis_logs'].append(log_entry)
                            
                            analysis_result = agent.analyze_new_file(current_novel, file_title, file_content)
                            st.write(f"📊 분석 결과: {len(analysis_result)} 항목")
                            
                            # 분석 완료 로그 저장
                            log_entry['status'] = '분석 완료'
                            log_entry['result_count'] = len(analysis_result)
                            st.session_state['ai_analysis_logs'][-1] = log_entry
                            
                            analysis_report = agent.get_analysis_report(analysis_result)
                            st.write("📋 분석 리포트 생성 완료")
                            
                            # 분석 결과를 세션 상태에 저장
                            st.session_state['last_analysis_result'] = analysis_result
                            st.session_state['last_analysis_report'] = analysis_report
                            st.session_state['show_analysis_result'] = True
                            
                            st.success(f'"{file_title}" 파일이 추가되었습니다. AI 분석이 완료되었습니다.')
                            
                            sync_novel_files(current_novel)
                            st.session_state['show_file_tabs'] = False
                            st.session_state['file_input_key'] += 1
                            st.session_state['show_edit_form'] = False
                            st.session_state['selected_file_idx'] = 0
                            st.session_state['selectbox_key_counter'] = st.session_state.get('selectbox_key_counter', 0) + 1
                            st.rerun()  # 분석 결과 표시를 위해 페이지 새로고침
                        else:
                            st.warning('제목을 입력해주세요.')

            # 파일 수정 폼은 show_edit_form이 True일 때만 표시
            if not show_tabs and st.session_state.get('show_edit_form', False) and selected_file_idx is not None and 0 <= selected_file_idx < len(files):
                st.markdown('---')
                st.subheader('파일 수정')
                edit_title = st.text_input('제목', value=files[selected_file_idx]['title'], key=f'edit_file_title_{current_novel}_{selected_file_idx}')
                edit_content = st.text_area('내용', value=files[selected_file_idx]['content'], key=f'edit_file_content_{current_novel}_{selected_file_idx}', height=200)
                if st.button('수정 확인', key=f'confirm_file_edit_{current_novel}_{selected_file_idx}'):
                    if edit_title.strip():
                        # 파일 시스템에도 반영
                        file_save_dir = db_dir / current_novel / 'Files'
                        file_save_dir.mkdir(parents=True, exist_ok=True)
                        file_path = file_save_dir / edit_title
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(edit_content)
                        sync_novel_files(current_novel)
                        st.success('파일이 수정 및 저장되었습니다.')
                        st.session_state['show_edit_form'] = False
                        st.session_state['selectbox_key_counter'] = st.session_state.get('selectbox_key_counter', 0) + 1
                        st.rerun()
                    else:
                        st.warning('제목을 입력해주세요.')

            # 파일 열람 UI (show_view_file이 True일 때만)
            if st.session_state.get('show_view_file', False) and selected_file_idx is not None and 0 <= selected_file_idx < len(files):
                st.markdown('---')
                st.subheader('파일 열람')
                st.markdown(f"**제목:** {files[selected_file_idx]['title']}")
                st.markdown(f"**내용:**\n\n{files[selected_file_idx]['content']}")
                # AI 분석 버튼 추가
                if st.button('🤖 AI 분석', key=f'analyze_file_{current_novel}_{selected_file_idx}', use_container_width=True):
                    file_title = files[selected_file_idx]['title']
                    file_content = files[selected_file_idx]['content']
                    st.session_state['ai_analysis_progress'] = []
                    def progress_callback(msg):
                        st.session_state['ai_analysis_progress'].append(msg)
                        st.session_state['ai_analysis_progress'] = st.session_state['ai_analysis_progress'][-30:]
                    with st.spinner('AI 분석 중입니다...'):
                        agent = OpenAINovelAnalysisAgent()
                        analysis_result = agent.analyze_new_file(current_novel, file_title, file_content, progress_callback=progress_callback)
                    analysis_report = agent.get_analysis_report(analysis_result)
                    st.session_state['last_analysis_result'] = analysis_result
                    st.session_state['last_analysis_report'] = analysis_report
                    st.session_state['show_analysis_result'] = True
                    log_entry = {
                        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'novel': current_novel,
                        'file': file_title,
                        'action': 'AI 분석',
                        'status': '분석 완료',
                        'result_count': len(analysis_result),
                        'analysis_result': analysis_result,
                        'analysis_report': analysis_report,
                        # 분석 결과 전체 세부 정보 추가
                        'characters': analysis_result.get('content_analysis', {}).get('characters', []),
                        'world_elements': analysis_result.get('content_analysis', {}).get('world_elements', []),
                        'events': analysis_result.get('content_analysis', {}).get('events', []),
                        'story_structure': analysis_result.get('content_analysis', {}).get('story_structure', {}),
                        'conflicts': analysis_result.get('conflicts', {}),
                        'recommendations': analysis_result.get('recommendations', {}),
                        'summary': analysis_result.get('summary', ''),
                        'file_name': analysis_result.get('file_name', ''),
                        'novel_name': analysis_result.get('novel_name', '')
                    }
                    st.session_state['ai_analysis_logs'].append(log_entry)
                    st.rerun()

    elif tab == '소설 스토리보드':
        current_novel = st.session_state.get('selected_novel', '')
        if current_novel:
            st.subheader('스토리보드 관리')
            
            # 스토리보드 데이터 관리
            if 'storyboards' not in st.session_state:
                st.session_state['storyboards'] = {}
            if current_novel not in st.session_state['storyboards']:
                st.session_state['storyboards'][current_novel] = []
            
            # 스토리보드 동기화 함수
            def sync_storyboards(novel_name):
                storyboard_dir = db_dir / novel_name / 'Storyboard'
                storyboards = []
                if storyboard_dir.exists():
                    for file in storyboard_dir.glob('*.json'):
                        if file.is_file():
                            try:
                                with open(file, 'r', encoding='utf-8') as f:
                                    import json
                                    data = json.load(f)
                                    storyboards.append(data)
                            except Exception as e:
                                pass
                st.session_state['storyboards'][novel_name] = storyboards
            
            # 초기 동기화
            sync_storyboards(current_novel)
            
            # 스토리보드 목록 표시
            storyboards = st.session_state['storyboards'].get(current_novel, [])
            
            # 상태 관리
            if 'show_chapter_form' not in st.session_state:
                st.session_state['show_chapter_form'] = False
            if 'editing_chapter_idx' not in st.session_state:
                st.session_state['editing_chapter_idx'] = None
            if 'show_scene_form' not in st.session_state:
                st.session_state['show_scene_form'] = False
            if 'selected_chapter_idx' not in st.session_state:
                st.session_state['selected_chapter_idx'] = None
            if 'editing_scene_idx' not in st.session_state:
                st.session_state['editing_scene_idx'] = None
            
            # 챕터 목록 표시
            if storyboards:
                st.markdown('### 챕터 목록')
                for i, chapter in enumerate(storyboards):
                    with st.expander(f"챕터 {i+1}: {chapter.get('title', '제목 없음')}", expanded=True):
                        st.markdown(f"**제목:** {chapter.get('title', '')}")
                        st.markdown(f"**내용:** {chapter.get('content', '')}")
                        
                        # 씬 목록 표시
                        scenes = chapter.get('scenes', [])
                        if scenes:
                            st.markdown("**씬 목록:**")
                            for j, scene in enumerate(scenes):
                                scene_name = scene.get('name', f'씬 {j+1}')
                                scene_desc = scene.get('description', '')
                                st.markdown(f"- **{scene_name}**: {scene_desc}")
                        
                        # 챕터 관리 버튼
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.button('챕터 수정', key=f'edit_chapter_{i}', use_container_width=True):
                                st.session_state['show_chapter_form'] = True
                                st.session_state['editing_chapter_idx'] = i
                                st.rerun()
                        with col2:
                            if st.button('+ 씬 추가', key=f'add_scene_to_chapter_{i}', use_container_width=True):
                                st.session_state['show_scene_form'] = True
                                st.session_state['selected_chapter_idx'] = i
                                st.session_state['editing_scene_idx'] = None
                                st.rerun()
                        with col3:
                            if st.button('챕터 삭제', key=f'delete_chapter_{i}', use_container_width=True):
                                # 파일 삭제
                                storyboard_dir = db_dir / current_novel / 'Storyboard'
                                storyboard_file = storyboard_dir / f'storyboard_{i+1}.json'
                                if storyboard_file.exists():
                                    storyboard_file.unlink()
                                sync_storyboards(current_novel)
                                st.success(f'챕터가 삭제되었습니다.')
                                st.rerun()
            
            # 챕터 추가/수정 폼
            if st.session_state.get('show_chapter_form', False):
                
                editing_idx = st.session_state.get('editing_chapter_idx', None)
                if editing_idx is not None:
                    st.subheader('챕터 수정')
                    chapter = storyboards[editing_idx]
                else:
                    st.subheader('새 챕터 추가')
                    chapter = {'title': '', 'content': '', 'scenes': []}
                
                # 제목과 내용 입력
                title = st.text_input('챕터 제목', value=chapter.get('title', ''), key='chapter_title')
                content = st.text_area('챕터 내용', value=chapter.get('content', ''), height=150, key='chapter_content')
                
                # 저장 버튼
                col1, col2 = st.columns(2)
                with col1:
                    if st.button('저장', key='save_chapter_btn'):
                        if title.strip():
                            # 챕터 데이터 준비
                            chapter_data = {
                                'title': title,
                                'content': content,
                                'scenes': chapter.get('scenes', [])
                            }
                            
                            # 파일 저장
                            storyboard_dir = db_dir / current_novel / 'Storyboard'
                            storyboard_dir.mkdir(parents=True, exist_ok=True)
                            
                            if editing_idx is not None:
                                # 수정
                                file_path = storyboard_dir / f'storyboard_{editing_idx+1}.json'
                            else:
                                # 새로 추가
                                file_path = storyboard_dir / f'storyboard_{len(storyboards)+1}.json'
                            
                            with open(file_path, 'w', encoding='utf-8') as f:
                                import json
                                json.dump(chapter_data, f, ensure_ascii=False, indent=2)
                            
                            sync_storyboards(current_novel)
                            st.session_state['show_chapter_form'] = False
                            st.session_state['editing_chapter_idx'] = None
                            st.success('챕터가 저장되었습니다.')
                            st.rerun()
                        else:
                            st.warning('챕터 제목을 입력해주세요.')
                
                with col2:
                    if st.button('취소', key='cancel_chapter_btn'):
                        st.session_state['show_chapter_form'] = False
                        st.session_state['editing_chapter_idx'] = None
                        st.rerun()
            
            # 씬 추가/수정 폼
            if st.session_state.get('show_scene_form', False):
                st.markdown('---')
                chapter_idx = st.session_state.get('selected_chapter_idx', None)
                editing_scene_idx = st.session_state.get('editing_scene_idx', None)
                
                if chapter_idx is not None and chapter_idx < len(storyboards):
                    chapter = storyboards[chapter_idx]
                    scenes = chapter.get('scenes', [])
                    
                    if editing_scene_idx is not None:
                        st.subheader(f'씬 수정 (챕터 {chapter_idx+1}: {chapter.get("title", "")})')
                        scene = scenes[editing_scene_idx]
                    else:
                        st.subheader(f'새 씬 추가 (챕터 {chapter_idx+1}: {chapter.get("title", "")})')
                        scene = {'name': '', 'description': ''}
                    
                    # 씬 이름과 설명 입력
                    scene_name = st.text_input('씬 이름', value=scene.get('name', ''), key='scene_name')
                    scene_description = st.text_area('씬 설명', value=scene.get('description', ''), height=100, key='scene_description')
                    
                    # 저장 버튼
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button('저장', key='save_scene_btn'):
                            if scene_name.strip() and scene_description.strip():
                                # 씬 데이터 업데이트
                                if editing_scene_idx is not None:
                                    scenes[editing_scene_idx]['name'] = scene_name.strip()
                                    scenes[editing_scene_idx]['description'] = scene_description.strip()
                                else:
                                    scenes.append({
                                        'name': scene_name.strip(),
                                        'description': scene_description.strip()
                                    })
                                
                                # 챕터 데이터 업데이트
                                chapter['scenes'] = scenes
                                
                                # 파일 저장
                                storyboard_dir = db_dir / current_novel / 'Storyboard'
                                file_path = storyboard_dir / f'storyboard_{chapter_idx+1}.json'
                                
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    import json
                                    json.dump(chapter, f, ensure_ascii=False, indent=2)
                                
                                sync_storyboards(current_novel)
                                st.session_state['show_scene_form'] = False
                                st.session_state['selected_chapter_idx'] = None
                                st.session_state['editing_scene_idx'] = None
                                st.success('씬이 저장되었습니다.')
                                st.rerun()
                            else:
                                st.warning('씬 이름과 설명을 모두 입력해주세요.')
                    
                    with col2:
                        if st.button('취소', key='cancel_scene_btn'):
                            st.session_state['show_scene_form'] = False
                            st.session_state['selected_chapter_idx'] = None
                            st.session_state['editing_scene_idx'] = None
                            st.rerun()
            
            # 새 챕터 추가 버튼
            if not st.session_state.get('show_chapter_form', False) and not st.session_state.get('show_scene_form', False):
                st.markdown('---')
                if st.button('새 챕터 추가', key='add_chapter_btn', use_container_width=True):
                    st.session_state['show_chapter_form'] = True
                    st.session_state['editing_chapter_idx'] = None
                    st.rerun()
        else:
            st.info('소설을 선택해주세요.')

    elif tab == '인물':
        current_novel = st.session_state.get('selected_novel', '')
        if current_novel:
            # 인물 포맷 설정 상태 관리
            if 'character_format' not in st.session_state:
                st.session_state['character_format'] = ['이름', '성별', '나이', '설명']
            if 'show_format_settings' not in st.session_state:
                st.session_state['show_format_settings'] = False
            if 'characters' not in st.session_state:
                st.session_state['characters'] = {}
            
            # 인물 동기화 함수
            def sync_characters(novel_name):
                character_dir = db_dir / novel_name / 'characters'
                characters = []
                if character_dir.exists():
                    for file in character_dir.glob('*.json'):
                        if file.is_file():
                            try:
                                with open(file, 'r', encoding='utf-8') as f:
                                    import json
                                    data = json.load(f)
                                    characters.append(data)
                            except Exception as e:
                                pass
                st.session_state['characters'][novel_name] = characters
            
            # 초기 동기화
            sync_characters(current_novel)
            
            # 헤더와 포맷 설정 버튼
            col1, col2 = st.columns([1, 0.1])
            with col1:
                st.markdown('### 인물 관리')
            with col2:
                if st.button('⚙', key='format_settings_btn', help='인물 포맷 설정', use_container_width=False):
                    st.session_state['show_format_settings'] = not st.session_state['show_format_settings']
                    st.rerun()
            
            # 인물 포맷 설정
            if st.session_state.get('show_format_settings', False):
                st.markdown('---')
                st.subheader('인물 포맷 설정')
                st.markdown('인물들이 공통적으로 가지는 속성을 설정하세요.')
                
                # 현재 포맷 표시 및 편집
                format_attributes = st.session_state['character_format'].copy()
                new_attributes = []
                
                for i, attr in enumerate(format_attributes):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        new_attr = st.text_input(f'속성 {i+1}', value=attr, key=f'format_attr_{i}')
                        if new_attr.strip():
                            new_attributes.append(new_attr.strip())
                    with col2:
                        if st.button('삭제', key=f'delete_attr_{i}'):
                            format_attributes.pop(i)
                            st.session_state['character_format'] = format_attributes
                            st.rerun()
                
                # 새 속성 추가
                new_attr = st.text_input('새 속성 추가', key='new_format_attr')
                if st.button('속성 추가', key='add_format_attr'):
                    if new_attr.strip() and new_attr.strip() not in format_attributes:
                        format_attributes.append(new_attr.strip())
                        st.session_state['character_format'] = format_attributes
                        st.rerun()
                
                # 저장 버튼
                col1, col2 = st.columns(2)
                with col1:
                    if st.button('포맷 저장', key='save_format_btn'):
                        st.session_state['character_format'] = new_attributes
                        st.success('인물 포맷이 저장되었습니다.')
                        st.rerun()
                with col2:
                    if st.button('기본값으로 초기화', key='reset_format_btn'):
                        st.session_state['character_format'] = ['이름', '성별', '나이', '설명']
                        st.success('기본 포맷으로 초기화되었습니다.')
                        st.rerun()
       
            # 인물 목록 표시
            characters = st.session_state['characters'].get(current_novel, [])
            character_dir = db_dir / current_novel / 'characters'
            character_files = list(character_dir.glob('*.json'))
            st.markdown('---')
            if characters:
                st.markdown('### 인물 목록')
                for i, (character, file_path) in enumerate(zip(characters, character_files)):
                    with st.expander(f"{character.get('이름', '이름 없음')}", expanded=True):
                        format_attrs = st.session_state['character_format']
                        for attr in format_attrs:
                            value = character.get(attr, '')
                            if value:
                                st.markdown(f"**{attr}:** {value}")
                        # 인물 관리 버튼
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button('인물 수정', key=f'edit_character_{i}', use_container_width=True):
                                st.session_state['show_character_form'] = True
                                st.session_state['editing_character_idx'] = i
                                st.rerun()
                        with col2:
                            if st.button('인물 삭제', key=f'delete_character_{i}', use_container_width=True):
                                if file_path.exists():
                                    file_path.unlink()
                                sync_characters(current_novel)
                                st.success(f'인물이 삭제되었습니다.')
                                st.rerun()
            
            # 인물 추가/수정 폼
            if st.session_state.get('show_character_form', False):
                st.markdown('---')
                editing_idx = st.session_state.get('editing_character_idx', None)
                if editing_idx is not None:
                    st.subheader('인물 수정')
                    character = characters[editing_idx]
                else:
                    st.subheader('새 인물 추가')
                    character = {}
                
                # 포맷에 따른 입력 필드 생성
                format_attrs = st.session_state['character_format']
                character_data = {}
                
                for attr in format_attrs:
                    value = character.get(attr, '')
                    if attr == '설명':
                        character_data[attr] = st.text_area(attr, value=value, height=100, key=f'character_{attr}')
                    else:
                        character_data[attr] = st.text_input(attr, value=value, key=f'character_{attr}')
                
                # 저장 버튼
                col1, col2 = st.columns(2)
                with col1:
                    if st.button('저장', key='save_character_btn'):
                        if character_data.get('이름', '').strip():
                            # 파일 저장
                            character_dir = db_dir / current_novel / 'characters'
                            character_dir.mkdir(parents=True, exist_ok=True)
                            
                            if editing_idx is not None:
                                # 수정
                                file_path = character_dir / f'character_{editing_idx+1}.json'
                            else:
                                # 새로 추가
                                file_path = character_dir / f'character_{len(characters)+1}.json'
                            
                            with open(file_path, 'w', encoding='utf-8') as f:
                                import json
                                json.dump(character_data, f, ensure_ascii=False, indent=2)
                            
                            sync_characters(current_novel)
                            st.session_state['show_character_form'] = False
                            st.session_state['editing_character_idx'] = None
                            st.success('인물이 저장되었습니다.')
                            st.rerun()
                        else:
                            st.warning('인물 이름을 입력해주세요.')
                
                with col2:
                    if st.button('취소', key='cancel_character_btn'):
                        st.session_state['show_character_form'] = False
                        st.session_state['editing_character_idx'] = None
                        st.rerun()
            
            # 새 인물 추가 버튼
            if not st.session_state.get('show_character_form', False):
                if st.button('새 인물 추가', key='add_character_btn', use_container_width=True):
                    st.session_state['show_character_form'] = True
                    st.session_state['editing_character_idx'] = None
                    st.rerun()
        else:
            st.info('소설을 선택해주세요.')

    elif tab == '세계관':
        current_novel = st.session_state.get('selected_novel', '')
        if current_novel:
            # 세계관 설정 상태 관리
            if 'world_settings' not in st.session_state:
                st.session_state['world_settings'] = {}
            if 'show_world_form' not in st.session_state:
                st.session_state['show_world_form'] = False
            if 'editing_world_idx' not in st.session_state:
                st.session_state['editing_world_idx'] = None
            
            # 세계관 동기화 함수
            def sync_world_settings(novel_name):
                world_dir = db_dir / novel_name / 'world'
                world_settings = []
                if world_dir.exists():
                    for file in world_dir.glob('*.json'):
                        if file.is_file():
                            try:
                                with open(file, 'r', encoding='utf-8') as f:
                                    import json
                                    data = json.load(f)
                                    world_settings.append(data)
                            except Exception as e:
                                pass
                st.session_state['world_settings'][novel_name] = world_settings
            
            # 초기 동기화
            sync_world_settings(current_novel)
            
            # 헤더와 카테고리 설정 버튼
            col1, col2 = st.columns([1, 0.1])
            with col1:
                st.markdown('### 세계관 설정')
            with col2:
                if st.button('⚙', key='world_category_settings_btn', help='카테고리 설정', use_container_width=False):
                    st.session_state['show_category_settings'] = not st.session_state.get('show_category_settings', False)
                    st.rerun()
            
            # 카테고리 설정 상태 관리
            if 'world_categories' not in st.session_state:
                st.session_state['world_categories'] = {
                    '시대 배경': '작품이 일어나는 시대나 연대',
                    '지리적 배경': '작품의 주요 장소나 지역',
                    '사회 구조': '작품 내 사회의 계급이나 구조',
                    '문화/종교': '작품 내 문화나 종교적 요소',
                    '기술/마법': '작품에서 사용되는 기술이나 마법 체계',
                    '정치/역사': '작품의 정치적 상황이나 역사적 배경',
                    '기타 설정': '기타 중요한 설정들'
                }
            
            # 카테고리 설정
            if st.session_state.get('show_category_settings', False):
                st.markdown('---')
                st.subheader('카테고리 설정')
                st.markdown('세계관 설정의 카테고리를 관리하세요.')
                
                # 현재 카테고리 표시 및 편집
                categories = st.session_state['world_categories'].copy()
                new_categories = {}
                
                for i, (category, description) in enumerate(categories.items()):
                    col1, col2, col3 = st.columns([2, 3, 1])
                    with col1:
                        new_category = st.text_input(f'카테고리 {i+1}', value=category, key=f'category_name_{i}')
                    with col2:
                        new_description = st.text_input(f'설명 {i+1}', value=description, key=f'category_desc_{i}')
                    with col3:
                        if st.button('삭제', key=f'delete_category_{i}'):
                            categories.pop(category)
                            st.session_state['world_categories'] = categories
                            st.rerun()
                    
                    if new_category.strip() and new_description.strip():
                        new_categories[new_category.strip()] = new_description.strip()
                
                # 새 카테고리 추가
                col1, col2 = st.columns([1, 1])
                with col1:
                    new_category = st.text_input('새 카테고리', key='new_category_name')
                with col2:
                    new_description = st.text_input('새 카테고리 설명', key='new_category_desc')
                
                if st.button('카테고리 추가', key='add_category_btn'):
                    if new_category.strip() and new_description.strip() and new_category.strip() not in categories:
                        categories[new_category.strip()] = new_description.strip()
                        st.session_state['world_categories'] = categories
                        st.rerun()
                
                # 저장 버튼
                col1, col2 = st.columns(2)
                with col1:
                    if st.button('카테고리 저장', key='save_categories_btn'):
                        st.session_state['world_categories'] = new_categories
                        st.success('카테고리가 저장되었습니다.')
                        st.rerun()
                with col2:
                    if st.button('기본값으로 초기화', key='reset_categories_btn'):
                        st.session_state['world_categories'] = {
                            '시대 배경': '작품이 일어나는 시대나 연대',
                            '지리적 배경': '작품의 주요 장소나 지역',
                            '사회 구조': '작품 내 사회의 계급이나 구조',
                            '문화/종교': '작품 내 문화나 종교적 요소',
                            '기술/마법': '작품에서 사용되는 기술이나 마법 체계',
                            '정치/역사': '작품의 정치적 상황이나 역사적 배경',
                            '기타 설정': '기타 중요한 설정들'
                        }
                        st.success('기본 카테고리로 초기화되었습니다.')
                        st.rerun()
                
                st.markdown('---')
            
            # 세계관 설정 목록 표시
            world_settings = st.session_state['world_settings'].get(current_novel, [])
            world_dir = db_dir / current_novel / 'world'
            world_files = list(world_dir.glob('*.json'))
            if world_settings:
                st.markdown('### 설정 목록')
                for i, (setting, file_path) in enumerate(zip(world_settings, world_files)):
                    with st.expander(f"{setting.get('title', '제목 없음')}", expanded=True):
                        st.markdown(f"**카테고리:** {setting.get('category', '')}")
                        st.markdown(f"**설명:** {setting.get('description', '')}")
                        st.markdown(f"**내용:** {setting.get('content', '')}")
                        # 설정 관리 버튼
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button('설정 수정', key=f'edit_world_{i}', use_container_width=True):
                                st.session_state['show_world_form'] = True
                                st.session_state['editing_world_idx'] = i
                                st.rerun()
                        with col2:
                            if st.button('설정 삭제', key=f'delete_world_{i}', use_container_width=True):
                                if file_path.exists():
                                    file_path.unlink()
                                sync_world_settings(current_novel)
                                st.success(f'설정이 삭제되었습니다.')
                                st.rerun()
            
            # 세계관 설정 추가/수정 폼
            if st.session_state.get('show_world_form', False):
                st.markdown('---')
                editing_idx = st.session_state.get('editing_world_idx', None)
                if editing_idx is not None:
                    st.subheader('설정 수정')
                    setting = world_settings[editing_idx]
                else:
                    
                    st.subheader('새 설정 추가')
                    setting = {'title': '', 'category': '', 'description': '', 'content': ''}
                
                # 기본 설정 카테고리들
                categories = st.session_state['world_categories']
                
                # 입력 필드
                title = st.text_input('설정 제목', value=setting.get('title', ''), key='world_title')
                category = st.selectbox('카테고리', list(categories.keys()), index=list(categories.keys()).index(setting.get('category', '시대 배경')) if setting.get('category') in categories else 0, key='world_category')
                description = st.text_input('설정 설명', value=setting.get('description', ''), key='world_description')
                content = st.text_area('설정 내용', value=setting.get('content', ''), height=200, key='world_content')
                
                # 저장 버튼
                col1, col2 = st.columns(2)
                with col1:
                    if st.button('저장', key='save_world_btn', use_container_width=True):
                        if title.strip() and content.strip():
                            # 설정 데이터 준비
                            setting_data = {
                                'title': title,
                                'category': category,
                                'description': description,
                                'content': content
                            }
                            
                            # 파일 저장
                            world_dir = db_dir / current_novel / 'world'
                            world_dir.mkdir(parents=True, exist_ok=True)
                            
                            if editing_idx is not None:
                                # 수정
                                file_path = world_dir / f'world_{editing_idx+1}.json'
                            else:
                                # 새로 추가
                                file_path = world_dir / f'world_{len(world_settings)+1}.json'
                            
                            with open(file_path, 'w', encoding='utf-8') as f:
                                import json
                                json.dump(setting_data, f, ensure_ascii=False, indent=2)
                            
                            sync_world_settings(current_novel)
                            st.session_state['show_world_form'] = False
                            st.session_state['editing_world_idx'] = None
                            st.success('설정이 저장되었습니다.')
                            st.rerun()
                        else:
                            st.warning('제목과 내용을 입력해주세요.')
                
                with col2:
                    if st.button('취소', key='cancel_world_btn', use_container_width=True):
                        st.session_state['show_world_form'] = False
                        st.session_state['editing_world_idx'] = None
                        st.rerun()
            
            # 새 설정 추가 버튼
            if not st.session_state.get('show_world_form', False):
                st.markdown('---')
                if st.button('새 설정 추가', key='add_world_btn', use_container_width=True):
                    st.session_state['show_world_form'] = True
                    st.session_state['editing_world_idx'] = None
                    st.rerun()
        else:
            st.info('소설을 선택해주세요.')

    elif tab == '타임라인':
        current_novel = st.session_state.get('selected_novel', '')
        if current_novel:
            # 타임라인 상태 관리
            if 'timeline_events' not in st.session_state:
                st.session_state['timeline_events'] = {}
            if 'show_timeline_form' not in st.session_state:
                st.session_state['show_timeline_form'] = False
            if 'editing_timeline_idx' not in st.session_state:
                st.session_state['editing_timeline_idx'] = None
            
            # 타임라인 동기화 함수
            def sync_timeline_events(novel_name):
                timeline_dir = db_dir / current_novel / 'Timeline'
                timeline_events = []
                if timeline_dir.exists():
                    for file in timeline_dir.glob('*.json'):
                        if file.is_file():
                            try:
                                with open(file, 'r', encoding='utf-8') as f:
                                    import json
                                    data = json.load(f)
                                    
                                    timeline_events.append(data)
                            except Exception as e:
                                pass
                st.session_state['timeline_events'][novel_name] = timeline_events
            
            # 초기 동기화
            sync_timeline_events(current_novel)
            
            # 헤더와 이벤트 추가 버튼
            col1, col2 = st.columns([1, 0.2])
            with col1:
                st.markdown('### 타임라인')
            with col2:
                if st.button('추가', key='add_timeline_btn', help='이벤트 추가', use_container_width=True):
                    st.session_state['show_timeline_form'] = True
                    st.session_state['editing_timeline_idx'] = None
                    st.rerun()
            
            # 타임라인 이벤트 추가/수정 폼
            if st.session_state.get('show_timeline_form', False):
                st.markdown('---')
                editing_idx = st.session_state.get('editing_timeline_idx', None)
                timeline_events = st.session_state['timeline_events'].get(current_novel, [])
                
                if editing_idx is not None:
                    st.subheader('이벤트 수정')
                    event = timeline_events[editing_idx]
                else:
                    st.subheader('새 이벤트 추가')
                    event = {'title': '', 'date': '', 'type': '명시적', 'description': '', 'importance': '보통'}
                
                # 입력 필드
                title = st.text_input('이벤트 제목', value=event.get('title', ''), key='timeline_title')
                
                col1, col2 = st.columns(2)
                with col1:
                    date = st.text_input('날짜/시기', value=event.get('date', ''), key='timeline_date', placeholder='예: 2023년, 3월, 과거 등')
                with col2:
                    event_type = st.selectbox('타입', ['명시적', '암묵적'], index=0 if event.get('type', '명시적') == '명시적' else 1, key='timeline_type')
                
                description = st.text_area('이벤트 설명', value=event.get('description', ''), height=150, key='timeline_description')
                
                col1, col2 = st.columns(2)
                with col1:
                    importance = st.selectbox('중요도', ['낮음', '보통', '높음', '매우 높음'], 
                                            index=['낮음', '보통', '높음', '매우 높음'].index(event.get('importance', '보통')), 
                                            key='timeline_importance')
                
                # 저장 버튼
                col1, col2 = st.columns(2)
                with col1:
                    if st.button('저장', key='save_timeline_btn', use_container_width=True):
                        if title.strip() and date.strip():
                            # 이벤트 데이터 준비
                            event_data = {
                                'title': title,
                                'date': date,
                                'type': event_type,
                                'description': description,
                                'importance': importance
                            }
                            
                            # 파일 저장
                            timeline_dir = db_dir / current_novel / 'Timeline'
                            timeline_dir.mkdir(parents=True, exist_ok=True)
                            
                            if editing_idx is not None:
                                # 수정
                                file_path = timeline_dir / f'timeline_{editing_idx+1}.json'
                            else:
                                # 새로 추가
                                file_path = timeline_dir / f'timeline_{len(timeline_events)+1}.json'
                            
                            with open(file_path, 'w', encoding='utf-8') as f:
                                import json
                                json.dump(event_data, f, ensure_ascii=False, indent=2)
                            
                            sync_timeline_events(current_novel)
                            st.session_state['show_timeline_form'] = False
                            st.session_state['editing_timeline_idx'] = None
                            st.success('이벤트가 저장되었습니다.')
                            st.rerun()
                        else:
                            st.warning('제목과 날짜를 입력해주세요.')
                
                with col2:
                    if st.button('취소', key='cancel_timeline_btn', use_container_width=True):
                        st.session_state['show_timeline_form'] = False
                        st.session_state['editing_timeline_idx'] = None
                        st.rerun()
            
            # 타임라인 이벤트 목록
            timeline_events = st.session_state['timeline_events'].get(current_novel, [])
            
            if timeline_events:
                # 명시적/암묵적 타임라인 분리
                explicit_events = [e for e in timeline_events if e.get('type') == '명시적']
                implicit_events = [e for e in timeline_events if e.get('type') == '암묵적']
                
                # 날짜 정렬 함수
                def sort_by_date(events):
                    def extract_date(event):
                        date_str = event.get('date', '')
                        # 숫자 추출 (연도, 월, 일 등)
                        import re
                        numbers = re.findall(r'\d+', date_str)
                        if numbers:
                            # 첫 번째 숫자를 기준으로 정렬 (연도 우선)
                            return int(numbers[0])
                        else:
                            # 숫자가 없으면 문자열 순서로 정렬
                            return 0
                    
                    return sorted(events, key=extract_date)
                
                # 명시적 타임라인 (날짜 순 정렬)
                if explicit_events:
                    explicit_events = sort_by_date(explicit_events)
                    st.markdown('### 📅 명시적 타임라인')
                    for i, event in enumerate(explicit_events):
                        with st.expander(f"{event.get('date', '')} - {event.get('title', '')}", expanded=True):
                            st.markdown(f"**날짜:** {event.get('date', '')}")
                            st.markdown(f"**설명:** {event.get('description', '')}")
                            st.markdown(f"**중요도:** {event.get('importance', '보통')}")
                            
                            # 이벤트 관리 버튼
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button('이벤트 수정', key=f'edit_explicit_{i}', use_container_width=True):
                                    st.session_state['show_timeline_form'] = True
                                    st.session_state['editing_timeline_idx'] = timeline_events.index(event)
                                    st.rerun()
                            with col2:
                                if st.button('이벤트 삭제', key=f'delete_explicit_{i}', use_container_width=True):
                                    # 파일 삭제 - 전체 이벤트 목록에서 해당 이벤트 찾기
                                    timeline_dir = db_dir / current_novel / 'Timeline'
                                    event_idx = timeline_events.index(event)
                                    timeline_file = timeline_dir / f'timeline_{event_idx+1}.json'
                                    if timeline_file.exists():
                                        timeline_file.unlink()
                                    
                                    # 파일 번호 재정렬
                                    remaining_files = list(timeline_dir.glob('*.json'))
                                    remaining_files.sort(key=lambda x: int(x.stem.split('_')[1]))
                                    
                                    for idx, file_path in enumerate(remaining_files, 1):
                                        new_name = f'timeline_{idx}.json'
                                        if file_path.name != new_name:
                                            file_path.rename(timeline_dir / new_name)
                                    
                                    sync_timeline_events(current_novel)
                                    st.success(f'이벤트가 삭제되었습니다.')
                                    st.rerun()
                
                # 암묵적 타임라인 (추가 순서대로)
                if implicit_events:
                    st.markdown('### 🕰️ 암묵적 타임라인')
                    for i, event in enumerate(implicit_events):
                        with st.expander(f"{event.get('date', '')} - {event.get('title', '')}", expanded=True):
                            st.markdown(f"**시기:** {event.get('date', '')}")
                            st.markdown(f"**설명:** {event.get('description', '')}")
                            st.markdown(f"**중요도:** {event.get('importance', '보통')}")
                            
                            # 이벤트 관리 버튼
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button('이벤트 수정', key=f'edit_implicit_{i}', use_container_width=True):
                                    st.session_state['show_timeline_form'] = True
                                    st.session_state['editing_timeline_idx'] = timeline_events.index(event)
                                    st.rerun()
                            with col2:
                                if st.button('이벤트 삭제', key=f'delete_implicit_{i}', use_container_width=True):
                                    # 파일 삭제 - 전체 이벤트 목록에서 해당 이벤트 찾기
                                    timeline_dir = db_dir / current_novel / 'Timeline'
                                    event_idx = timeline_events.index(event)
                                    timeline_file = timeline_dir / f'timeline_{event_idx+1}.json'
                                    if timeline_file.exists():
                                        timeline_file.unlink()
                                    
                                    # 파일 번호 재정렬
                                    remaining_files = list(timeline_dir.glob('*.json'))
                                    remaining_files.sort(key=lambda x: int(x.stem.split('_')[1]))
                                    
                                    for idx, file_path in enumerate(remaining_files, 1):
                                        new_name = f'timeline_{idx}.json'
                                        if file_path.name != new_name:
                                            file_path.rename(timeline_dir / new_name)
                                    
                                    sync_timeline_events(current_novel)
                                    st.success(f'이벤트가 삭제되었습니다.')
                                    st.rerun()
                
                # 타임라인 시각화
                # 예시 색상 매핑
                color_map = {'낮음': '#90EE90', '보통': '#FFD700', '높음': '#FF8C00', '매우 높음': '#FF0000'}

                if explicit_events:
                    sorted_explicit_events = sort_by_date(explicit_events)

                    # 모든 이벤트는 y = 0 위치에
                    y_value = 0

                    fig = go.Figure()

                    # 1️⃣ 타임라인 수평선 추가
                    x_dates = [event.get('date', '') for event in sorted_explicit_events]
                    if x_dates:
                        x_dates_sorted = sorted(x_dates)
                        fig.add_trace(go.Scatter(
                            x=x_dates_sorted,
                            y=[y_value] * len(x_dates_sorted),
                            mode='lines',
                            line=dict(color='gray', width=2),
                            hoverinfo='skip',
                            showlegend=False
                        ))

                    # 2️⃣ 각 이벤트 점 추가
                    for event in sorted_explicit_events:
                        date = event.get('date', '')
                        title = event.get('title', '')
                        importance = event.get('importance', '보통')
                        description = event.get('description', '')

                        fig.add_trace(go.Scatter(
                            x=[date],
                            y=[y_value],
                            mode='markers+text',
                            marker=dict(
                                size=16,
                                color=color_map.get(importance, '#FFD700'),
                                symbol='circle'
                            ),
                            text=[title],
                            textposition='top center',
                            hovertemplate=f"<b>{title}</b><br>날짜: {date}<br>중요도: {importance}<br>설명: {description}<extra></extra>"
                        ))

                    # 3️⃣ 레이아웃 설정
                    fig.update_layout(
                        title='명시적 타임라인',
                        xaxis_title='날짜/시기',
                        yaxis=dict(
                            title='',
                            showticklabels=False,
                            showgrid=False,
                            zeroline=False,
                            range=[-1, 1],          # y축 고정
                            fixedrange=True         # y축 줌/팬 방지
                        ),
                        shapes=[                    # 👇 수평선 고정 추가
                            dict(
                                type="line",
                                xref="paper", x0=0, x1=1,
                                yref="y", y0=0, y1=0,
                                line=dict(color="gray", width=2)
                            )
                        ],
                        height=350,
                        showlegend=False,
                        margin=dict(t=60, b=40)
                    )

                    st.plotly_chart(fig, use_container_width=True)
                
                # 암묵적 타임라인 그래프
                
            else:
                st.info('타임라인 이벤트가 없습니다. + 버튼을 눌러 이벤트를 추가해보세요.')
        else:
            st.info('소설을 선택해주세요.')

    # 하단 여백 추가
    st.markdown("<br><br>", unsafe_allow_html=True)

# --- 우측: AI 대화 영역 ---
with right_col:
    st.header('SomnniAI')
    # 기존 채팅 기능
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    # 대화창(헤더 아래~입력창 위까지 height:70vh)
    chat_html = """
    <div style='height:90vh; min-height:90vh; display:flex; flex-direction:column; position:relative; background:rgba(227,230,234,0.95); border-radius:20px 0 0 20px; margin-top:0.2rem;'>
      <div id='chat-scroll-area' style='flex:1 1 0%; min-height:0; overflow-y:auto; display:flex; flex-direction:column; gap:1.1rem; padding:0.7rem 0.5rem 0.2rem 0.5rem;'>
    """
    for msg in st.session_state['chat_history']:
        if msg['role'] == 'user':
            chat_html += f"""
            <div style='display: flex; justify-content: flex-end;'>
                <div style='background: #2a3b8f; color: white; padding: 0.7rem 1.2rem; border-radius: 18px 18px 4px 18px; max-width: 70%; word-break: break-all; font-size: 1.05rem;'>
                    {msg['content']}
                </div>
            </div>
            """
        else:
            chat_html += f"""
            <div style='display: flex; justify-content: flex-start;'>
                <div style='background: #fff; color: #222; padding: 0.7rem 1.2rem; border-radius: 18px 18px 18px 4px; max-width: 70%; word-break: break-all; font-size: 1.05rem; border: 1px solid #d1d5db;'>
                    {msg['content']}
                </div>
            </div>
            """
    chat_html += """
      </div>
      <script>
        var chatArea = document.getElementById('chat-scroll-area');
        if (chatArea) {
          chatArea.scrollTop = chatArea.scrollHeight;
        }
      </script>
    </div>
    """
    import streamlit.components.v1 as components
    components.html(chat_html, height=550, scrolling=True)
    # 입력창은 대화창 바로 아래에 자연스럽게
    st.markdown("""
    <div style='width:100%; display: flex; flex-direction: column; justify-content: flex-end; margin-top:0.2rem; flex-shrink:0;'>
    """, unsafe_allow_html=True)
    user_input = st.text_input('메시지 입력', '', key=f'chat_input_{len(st.session_state["chat_history"])}', label_visibility='collapsed', placeholder='메시지를 입력하세요...')
    st.markdown("""
    </div>
    """, unsafe_allow_html=True)
    if user_input:
        # 답변 생성: SomnniAI 사용
        from Agent.openai_agent import SomnniAI
        ai = SomnniAI()
        novel_name = st.session_state.get('selected_novel', '')
        answer = ai.answer_query(novel_name, user_input)
        st.session_state['chat_history'].append({'role': 'user', 'content': user_input})
        st.session_state['chat_history'].append({'role': 'ai', 'content': answer})
        st.rerun()
    # 우측 컬럼 하단 여백 추가
    st.markdown("<br><br>", unsafe_allow_html=True)

# --- 하단: AI 분석 결과 표시 ---
if st.session_state.get('show_analysis_result', False):
    st.markdown("---")
    st.markdown("## 🤖 AI 분석 결과")
    
    # 분석 결과 요약
    analysis_result = st.session_state.get('last_analysis_result', {})
    if 'summary' in analysis_result:
        st.info(analysis_result['summary'])
    
    # 상세 분석 결과
    with st.expander("🔍 상세 분석 보기", expanded=True):
        if 'content_analysis' in analysis_result:
            content_analysis = analysis_result['content_analysis']
            
            # 인물 분석
            if content_analysis.get('characters'):
                st.markdown("**👥 발견된 인물:**")
                for char in content_analysis['characters'][:5]:  # 상위 5명만
                    role = char.get('role', '미정')
                    personality = char.get('personality', '')
                    background = char.get('background', '')
                    st.markdown(f"- **{char.get('name', 'Unknown')}** ({role})")
                    if personality:
                        st.markdown(f"  - 성격: {personality}")
                    if background:
                        st.markdown(f"  - 배경: {background}")
            
            # 세계관 요소
            if content_analysis.get('world_elements'):
                st.markdown("**🌍 세계관 요소:**")
                for element in content_analysis['world_elements'][:3]:  # 상위 3개만
                    category = element.get('category', '기타')
                    description = element.get('description', '')
                    st.markdown(f"- **{element.get('name', 'Unknown')}** ({category})")
                    if description:
                        st.markdown(f"  - {description}")
            
            # 이벤트
            if content_analysis.get('events'):
                st.markdown("**📅 발견된 이벤트:**")
                for event in content_analysis['events'][:3]:  # 상위 3개만
                    date = event.get('date', '날짜 미정')
                    title = event.get('title', '제목 없음')
                    importance = event.get('importance', '보통')
                    desc = event.get('description', '')[:100] + '...' if len(event.get('description', '')) > 100 else event.get('description', '')
                    st.markdown(f"- **{title}** ({date}, 중요도: {importance})")
                    if desc:
                        st.markdown(f"  - {desc}")
            
            # 스토리 구조
            if content_analysis.get('story_structure'):
                story_structure = content_analysis['story_structure']
                st.markdown("**📖 스토리 구조:**")
                if story_structure.get('conflict'):
                    st.markdown(f"- 갈등: {story_structure['conflict']}")
                if story_structure.get('resolution'):
                    st.markdown(f"- 해결: {story_structure['resolution']}")
                if story_structure.get('pacing'):
                    st.markdown(f"- 전개 속도: {story_structure['pacing']}")
    
    # 모순 분석 결과
    conflicts = analysis_result.get('conflicts', {})
    # 실제 모순만 체크 (새로운 정보는 문제가 아님)
    has_contradictions = (
        conflicts.get('internal_contradictions') or 
        conflicts.get('external_contradictions')
    )
    if has_contradictions:
        st.markdown("### 🔍 모순 분석")
        
        # 심각도별 색상 매핑
        severity_colors = {
            "심각": "🔴",
            "보통": "🟡", 
            "경미": "🟢"
        }
        
        # 내부 모순 표시
        if 'internal_contradictions' in conflicts and conflicts['internal_contradictions']:
            st.markdown("#### 📖 내부 모순 (소설 내용 내)")
            for i, contradiction in enumerate(conflicts['internal_contradictions']):
                severity_icon = severity_colors.get(contradiction.get('severity', '보통'), '🟡')
                st.markdown(f"**{severity_icon} {contradiction.get('type', '모순')} - {contradiction.get('description', '')[:50]}...**")
                st.markdown(f"- 유형: {contradiction.get('type', '')}")
                st.markdown(f"- 설명: {contradiction.get('description', '')}")
                st.markdown(f"- 심각도: {severity_icon} {contradiction.get('severity', '')}")
                if contradiction.get('elements'):
                    st.markdown("- 모순되는 요소:")
                    for element in contradiction['elements']:
                        st.markdown(f"    - {element}")
                if contradiction.get('suggestion'):
                    st.markdown(f"- 해결 방안: {contradiction['suggestion']}")
    
        # 외부 모순 표시
        if 'external_contradictions' in conflicts and conflicts['external_contradictions']:
            st.markdown("#### 🗄️ 외부 모순 (기존 설정과)")
            for i, contradiction in enumerate(conflicts['external_contradictions']):
                severity_icon = severity_colors.get(contradiction.get('severity', '보통'), '🟡')
                st.markdown(f"**{severity_icon} {contradiction.get('type', '모순')} - {contradiction.get('description', '')[:50]}...**")
                st.markdown(f"- 유형: {contradiction.get('type', '')}")
                st.markdown(f"- 설명: {contradiction.get('description', '')}")
                st.markdown(f"- 심각도: {severity_icon} {contradiction.get('severity', '')}")
                if contradiction.get('new_element'):
                    st.markdown(f"- 새로운 내용: {contradiction['new_element']}")
                if contradiction.get('existing_element'):
                    st.markdown(f"- 기존 설정: {contradiction['existing_element']}")
                if contradiction.get('suggestion'):
                    st.markdown(f"- 해결 방안: {contradiction['suggestion']}")
    
        # 기존 충돌 분석 결과 표시 (하위 호환성)
        if 'character_conflicts' in conflicts and conflicts['character_conflicts']:
            st.markdown("#### ⚠️ 기존 충돌 분석 (하위 호환)")
            for conflict in conflicts['character_conflicts'][:3]:  # 상위 3개만
                st.warning(f"**인물 충돌:** {conflict.get('new_character', '')} vs {conflict.get('existing_character', '')} - {conflict.get('description', '')}")
    
        if 'world_setting_conflicts' in conflicts and conflicts['world_setting_conflicts']:
            for conflict in conflicts['world_setting_conflicts'][:3]:  # 상위 3개만
                st.warning(f"**세계관 충돌:** {conflict.get('new_element', '')} vs {conflict.get('existing_element', '')} - {conflict.get('description', '')}")
    
        if 'timeline_conflicts' in conflicts and conflicts['timeline_conflicts']:
            for conflict in conflicts['timeline_conflicts'][:3]:  # 상위 3개만
                st.warning(f"**타임라인 충돌:** {conflict.get('new_event', '')} vs {conflict.get('existing_event', '')} - {conflict.get('description', '')}")
    else:
        st.info("✅ 모순 없음 - 내용상 모순이 발견되지 않았습니다.")
    
    # 추천 사항
    recommendations = analysis_result.get('recommendations', {})
    if any(recommendations.values()):
        st.markdown("### 💡 AI 추천 사항")
        
        total_recommendations = sum(len(recs) for recs in recommendations.values())
        st.success(f"총 {total_recommendations}개의 추천 사항이 있습니다.")
        
        # 각 카테고리별 추천
        if recommendations.get('storyboard_suggestions'):
            with st.expander("📝 스토리보드 발전 방향", expanded=True):
                for suggestion in recommendations['storyboard_suggestions'][:3]:
                    st.markdown(f"- {suggestion}")
        
        if recommendations.get('character_suggestions'):
            with st.expander("👤 인물 설정 보완", expanded=True):
                for suggestion in recommendations['character_suggestions'][:3]:
                    st.markdown(f"- {suggestion}")
        
        if recommendations.get('world_setting_suggestions'):
            with st.expander("🌍 세계관 설정 확장", expanded=True):
                for suggestion in recommendations['world_setting_suggestions'][:3]:
                    st.markdown(f"- {suggestion}")
        
        if recommendations.get('timeline_suggestions'):
            with st.expander("📅 타임라인 구성 개선", expanded=True):
                for suggestion in recommendations['timeline_suggestions'][:3]:
                    st.markdown(f"- {suggestion}")
    
    # --- 정보 추출 버튼 및 추천 업데이트 UI ---
    if 'info_extract_clicked' not in st.session_state:
        st.session_state['info_extract_clicked'] = False
    if st.button('정보 추출', key='extract_info_btn', use_container_width=True):
        # 정보 추출 세션 값 초기화(항상 최신 정보로 추출)
        for key in ['new_characters', 'new_world_elements', 'new_timeline', 'new_storyboard']:
            if key in st.session_state:
                del st.session_state[key]
        # character_format이 없으면 경고만 띄우고, 초기화는 하지 않음
        if 'character_format' not in st.session_state:
            st.warning('인물 포맷이 설정되어 있지 않습니다. 인물 탭에서 먼저 포맷을 설정하세요.')
        st.session_state['info_extract_clicked'] = True
        st.rerun()
    
    if st.session_state.get('info_extract_clicked', False):
        st.markdown('### 📝 추천 업데이트')

        from Agent.openai_agent import OpenAINovelAnalysisAgent
        from Agent.Agent import NovelAnalysisAgent
        agent = NovelAnalysisAgent()
        openai_agent = OpenAINovelAnalysisAgent()
        db_dir = "Database"
        novel_name = st.session_state.get('selected_novel', '')

        # DB 데이터 로드
        char_db = agent.db_manager.get_characters(novel_name)
        world_db = agent.db_manager.get_world_settings(novel_name)
        timeline_db = agent.db_manager.get_timeline_events(novel_name)
        storyboard_db = agent.db_manager.get_storyboards(novel_name)
        categories = st.session_state.get('categories', {})
        category_list = list(categories.keys()) if categories else ["기타"]
        analysis_result = st.session_state.get('last_analysis_result', {})

        # --- 정보 추출 시 스피너 표시 ---
        with st.spinner('정보 추출 중입니다...'):
            # --- 세션 상태에 신규 항목 저장 (최초 1회만) ---
            if 'new_characters' not in st.session_state:
                if 'character_format' in st.session_state:
                    char_format = st.session_state['character_format']
                    char_format_example = {k: f"예시 {k}" for k in char_format}
                    st.session_state['new_characters'] = openai_agent.extract_new_characters_with_openai(
                        analysis_result, char_db, char_format_example
                    )
                else:
                    st.session_state['new_characters'] = []
            if 'new_world_elements' not in st.session_state:
                st.session_state['new_world_elements'] = openai_agent.extract_new_world_elements_with_openai(
                    analysis_result, world_db, category_list
                )
            if 'new_timeline' not in st.session_state:
                st.session_state['new_timeline'] = openai_agent.extract_new_timeline_with_openai(
                    analysis_result, timeline_db
                )
            if 'new_storyboard' not in st.session_state:
                st.session_state['new_storyboard'] = openai_agent.extract_new_storyboard_with_openai(
                    analysis_result, storyboard_db
                )

        # --- 적용/취소 시 리스트에서 즉시 제거하는 함수 ---
        def show_apply_cancel_ui(item, item_type, idx, session_key):
            # 사람이 읽기 쉬운 요약만 출력
            if item_type == "character":
                st.markdown(f"**이름:** {item.get('이름', item.get('name', ''))}")
                for k, v in item.items():
                    if k not in ['이름', 'name']:
                        st.markdown(f"- **{k}:** {v}")
            elif item_type == "world":
                st.markdown(f"**제목:** {item.get('title', item.get('name', ''))}")
                st.markdown(f"- **카테고리:** {item.get('category', '')}")
                st.markdown(f"- **설명:** {item.get('description', '')}")
            elif item_type == "timeline":
                st.markdown(f"**제목:** {item.get('title', '')}")
                st.markdown(f"- **날짜:** {item.get('date', '')}")
                st.markdown(f"- **설명:** {item.get('description', '')}")
                st.markdown(f"- **중요도:** {item.get('importance', '')}")
                st.markdown(f"- **명시적 이벤트:** {'✅' if item.get('explicit_events', False) else '❌'}")
            elif item_type == "storyboard":
                st.markdown(f"**제목:** {item.get('title', '')}")
                st.markdown(f"- **설명:** {item.get('description', '')}")
            col1, col2 = st.columns(2)
            if col1.button("적용", key=f"apply_{item_type}_{idx}"):
                # DB에 저장
                if item_type == "character":
                    agent.db_manager.save_character(novel_name, item)
                elif item_type == "world":
                    agent.db_manager.save_world_setting(novel_name, item)
                elif item_type == "timeline":
                    agent.db_manager.save_timeline_event(novel_name, item)
                elif item_type == "storyboard":
                    agent.db_manager.save_storyboard(novel_name, item)
                st.session_state[session_key].pop(idx)
                st.rerun()
            if col2.button("취소", key=f"cancel_{item_type}_{idx}"):
                st.session_state[session_key].pop(idx)
                st.rerun()

        # 인물
        if st.session_state['new_characters']:
            st.markdown("#### 👤 신규 인물")
            for idx, char in enumerate(st.session_state['new_characters']):
                if not isinstance(char, dict):
                    continue
                show_apply_cancel_ui(char, "character", idx, 'new_characters')
        else:
            st.info('신규 인물 추천이 없습니다.')


        # 세계관
        if st.session_state['new_world_elements']:
            st.markdown("#### 🌍 신규 세계관 요소")
            for idx, element in enumerate(st.session_state['new_world_elements']):
                if not isinstance(element, dict):
                    continue
                # category_list가 None이거나 비어있으면 기본값 사용
                safe_category_list = category_list if category_list else ["기타"]
                display_name = element.get('title') or element.get('name') or f"세계관 요소 {idx+1}"
                category = element.get('category', safe_category_list[0]) if isinstance(element, dict) else safe_category_list[0]
                element['category'] = st.selectbox(
                    display_name,
                    safe_category_list,
                    index=safe_category_list.index(category) if category in safe_category_list else 0,
                    key=f"world_category_{idx}"
                )
                show_apply_cancel_ui(element, "world", idx, 'new_world_elements')

        # 타임라인
        if st.session_state['new_timeline']:
            st.markdown("#### ⏳ 신규 타임라인 이벤트")
            for idx, event in enumerate(st.session_state['new_timeline']):
                if not isinstance(event, dict):
                    continue
                show_apply_cancel_ui(event, "timeline", idx, 'new_timeline')

        # 스토리보드
        if st.session_state['new_storyboard']:
            st.markdown("#### 📝 신규 스토리보드(씬)")
            for idx, scene in enumerate(st.session_state['new_storyboard']):
                if not isinstance(scene, dict):
                    continue
                show_apply_cancel_ui(scene, "storyboard", idx, 'new_storyboard')

    st.markdown('---')


