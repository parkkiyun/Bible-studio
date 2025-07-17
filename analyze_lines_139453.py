import requests
from bs4 import BeautifulSoup
import re

def analyze_lines_139453():
    """139453 게시글의 줄별 분석"""
    
    url = "https://nocr.net/com_kor_hochma/139453"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"🔍 {url} 줄별 분석 중...")
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        content_element = soup.find(class_='xe_content') or soup.find(class_='rd_body') or soup.find(class_='rhymix_content')
        
        if content_element:
            content_text = content_element.get_text(strip=True)
            lines = content_text.split('\n')
            
            print(f"📄 총 줄 수: {len(lines)}")
            
            # 절 구분자 패턴들
            patterns = [
                r'^(\d+):(\d+)$',                      # 19:11
                r'^(\d+):(\d+(?:,\d+)+)$',             # 19:23,24
                r'^(\d+):(\d+)-(\d+)$',                # 19:10-14
            ]
            
            verse_separators = []
            
            print(f"\n🔍 각 줄 분석 (처음 50줄):")
            for i, line in enumerate(lines[:50]):
                stripped_line = line.strip()
                
                if stripped_line:  # 빈 줄이 아닌 경우만
                    is_separator = False
                    matched_pattern = None
                    
                    for j, pattern in enumerate(patterns):
                        match = re.match(pattern, stripped_line)
                        if match:
                            is_separator = True
                            matched_pattern = j
                            verse_separators.append((i, stripped_line, match.groups()))
                            break
                    
                    status = "✅ 절구분자" if is_separator else "📝 내용"
                    print(f"  [{i+1:3}] {status} | '{stripped_line[:60]}{'...' if len(stripped_line) > 60 else ''}'")
                    
                    if is_separator:
                        print(f"       -> 패턴 {matched_pattern}: {match.groups()}")
                
                elif i < 50:  # 빈 줄도 처음 50개 안에서는 표시
                    print(f"  [{i+1:3}] 📭 빈줄   | ''")
            
            if len(lines) > 50:
                print(f"\n... (총 {len(lines)}줄 중 처음 50줄만 표시)")
            
            print(f"\n📊 전체 절 구분자 찾기:")
            all_verse_separators = []
            
            for i, line in enumerate(lines):
                stripped_line = line.strip()
                if stripped_line:
                    for pattern in patterns:
                        match = re.match(pattern, stripped_line)
                        if match:
                            all_verse_separators.append((i, stripped_line, match.groups()))
                            break
            
            print(f"총 {len(all_verse_separators)}개 절 구분자 발견:")
            for i, (line_idx, line_text, groups) in enumerate(all_verse_separators):
                print(f"  [{i+1}] 줄 {line_idx+1}: '{line_text}' -> {groups}")
                
                # 다음 몇 줄의 내용도 확인
                if line_idx + 1 < len(lines):
                    next_lines = []
                    for j in range(1, min(4, len(lines) - line_idx)):
                        next_line = lines[line_idx + j].strip()
                        if next_line:
                            next_lines.append(next_line[:50])
                        if len(next_lines) >= 2:
                            break
                    if next_lines:
                        print(f"       다음 내용: {' | '.join(next_lines)}...")
            
    except Exception as e:
        print(f"❌ 분석 실패: {e}")

if __name__ == "__main__":
    analyze_lines_139453() 