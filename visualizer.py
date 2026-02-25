import streamlit as st


def render_grid_animation(rows, cols, emoji):
    """
    주어진 행(rows)열(cols) 수만큼 이모지를 HTML/CSS/JS로 렌더링하여 애니메이션과 함께 표시합니다.
    """

    # CSS 설정 (그리드 레이아웃 및 애니메이션)
    # 항상 9열 짜리 그리드를 고정 크기로 렌더링
    html_content = f"""
    <style>
        .grid-container {{
            display: grid;
            grid-template-columns: repeat(9, 1fr);
            gap: 2px;
            justify-content: center;
            align-items: center;
            margin: 0 auto;
            max-width: 320px; /* 스마트폰 세로 높이에 맞춰 가로폭 더 축소 */
        }}
        .grid-item {{
            aspect-ratio: 1 / 1; /* 완벽한 정사각형 유지 */
            background-color: #f7f9fc; /* 기본 옅은 빈칸 배경 */
            border: 1px dotted #dce2eb; /* 기본 옅은 테두리 */
            border-radius: 8px; /* 둥근 모서리 */
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: clamp(1rem, 5vw, 1.8rem); /* 9개 고정이므로 글씨 크기 적당히 고정 */
            color: transparent; /* 초기엔 이모지 안 보이게 */
            position: relative;
        }}
        /* 정답에 해당하는 부분만 스타일 변경 및 등장 애니메이션 */
        .grid-item.active {{
            background-color: #FFF9CE;
            border: 2px solid #FFC93C;
            box-shadow: inset 0 0 5px rgba(0,0,0,0.05);
            color: inherit;
        }}
        .emoji-wrapper {{
            opacity: 0;
            transform: scale(0);
            transition: opacity 0.2s ease, transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }}
        .emoji-wrapper.show {{
            opacity: 1;
            transform: scale(1);
        }}
    </style>

    <div class="grid-container" id="emoji-grid">
        <!-- 9x9 = 81개의 이모지/빈공간 -->
    </div>

    <script>
        setTimeout(function() {{
            const grid = document.getElementById('emoji-grid');
            grid.innerHTML = ''; // 초기화
            
            // 항상 9행 9열 (81개)의 프레임을 고정 생성
            for (let r = 0; r < 9; r++) {{
                for (let c = 0; c < 9; c++) {{
                    const item = document.createElement('div');
                    item.className = 'grid-item';
                    
                    // 현재 칸이 출제된 rows x cols 안에 포함되는 범위인지 확인
                    const isTarget = (r < {rows}) && (c < {cols});
                    
                    if (isTarget) {{
                        item.classList.add('active'); // 테두리/배경 활성화
                        item.innerHTML = '<div class="emoji-wrapper">{emoji}</div>';
                    }} else {{
                        // 범위 밖은 희미하게 빈 칸만 유지 (이모지 없음)
                        item.innerHTML = '';
                    }}
                    
                    grid.appendChild(item);
                }}
            }}

            // 애니메이션 지연 적용 (활성화된 놈들만 하나씩 뾰로롱)
            const activeWrappers = document.querySelectorAll('.emoji-wrapper');
            activeWrappers.forEach((wrapper, index) => {{
                setTimeout(() => {{
                    wrapper.classList.add('show');
                }}, index * 15); // 좀 더 빠르게 0.015초 간격
            }});
        }}, 100);
    </script>
    """

    # 전체 그리드 높이도 스마트폰에 맞춰 축소
    st.components.v1.html(html_content, height=340)


# 테스트용 코드 (직접 실행할 때만)
if __name__ == "__main__":
    st.title("비주얼라이저 테스트")
    render_grid_animation(5, 3, "🍎")
