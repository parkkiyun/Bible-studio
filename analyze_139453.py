import requests
from bs4 import BeautifulSoup
import re

def analyze_139453():
    """139453 게시글 패턴 분석"""
    
    url = "https://nocr.net/com_kor_hochma/139453"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"🔍 {url} 분석 중...")
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        content_element = soup.find(class_='xe_content') or soup.find(class_='rd_body') or soup.find(class_='rhymix_content')
        
        if content_element:
            content_text = content_element.get_text(strip=True)
            
            print(f"📄 전체 텍스트 길이: {len(content_text)}자")
            
            # 다양한 패턴들을 확인
            patterns = {
                'equals_4': r'====(\d+):(\d+)',                    # ====31:1
                'equals_3': r'===(\d+):(\d+)',                     # ===31:1
                'equals_any': r'={3,}(\d+):(\d+)',                 # 3개 이상 등호
                'line_start': r'^(\d+):(\d+)$',                    # 줄 시작의 19:1
                'comma_verses': r'^(\d+):(\d+(?:,\d+)+)$',         # 19:37,38 (새 패턴!)
                'single_comma': r'(\d+):(\d+,\d+)',                # 19:37,38 (일반 위치)
            }
            
            print(f"\n🔍 패턴 분석:")
            lines = content_text.split('\n')
            
            for pattern_name, pattern in patterns.items():
                if pattern_name in ['line_start', 'comma_verses']:
                    # 줄 단위로 매칭
                    matches = []
                    for i, line in enumerate(lines):
                        line = line.strip()
                        match = re.match(pattern, line)
                        if match:
                            matches.append((i, line, match.groups()))
                    
                    if matches:
                        print(f"✅ {pattern_name}: {len(matches)}개 매치")
                        for i, (line_idx, line_text, groups) in enumerate(matches[:5]):  # 처음 5개만 표시
                            print(f"   [{i+1}] 줄 {line_idx+1}: '{line_text}' -> {groups}")
                else:
                    # 전체 텍스트에서 매칭
                    matches = re.findall(pattern, content_text)
                    if matches:
                        print(f"✅ {pattern_name}: {len(matches)}개 매치")
                        for i, match in enumerate(matches[:5]):  # 처음 5개만 표시
                            print(f"   [{i+1}] {match}")
            
            # 콤마가 포함된 절 번호들을 구체적으로 찾기
            print(f"\n🔍 콤마 포함 절 번호 검색:")
            comma_pattern = r'\b\d+:\d+(?:,\d+)+\b'
            comma_matches = re.findall(comma_pattern, content_text)
            if comma_matches:
                print(f"발견된 콤마 절 번호들: {comma_matches}")
                
                # 실제 위치와 내용 확인
                for match in comma_matches[:3]:  # 처음 3개만 자세히 보기
                    match_index = content_text.find(match)
                    context_start = max(0, match_index - 50)
                    context_end = min(len(content_text), match_index + len(match) + 200)
                    context = content_text[context_start:context_end]
                    print(f"\n📝 '{match}' 주변 내용:")
                    print(f"   {context}")
            else:
                print("콤마 포함 절 번호를 찾을 수 없습니다.")
            
    except Exception as e:
        print(f"❌ 분석 실패: {e}")

if __name__ == "__main__":
    analyze_139453() 