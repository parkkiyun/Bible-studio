import requests
from bs4 import BeautifulSoup
import re

def test_verse_pattern():
    """
    호크마 사이트에서 절 구분 패턴 분석
    """
    url = "https://nocr.net/com_kor_hochma/139477"  # 창세기 31장
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print(f"페이지 분석: {url}")
    print("=" * 60)
    
    # 제목 확인
    title = ""
    for h1 in soup.find_all('h1'):
        h1_text = h1.get_text(strip=True)
        if '주석' in h1_text:
            title = h1_text
            break
    
    print(f"제목: {title}")
    
    # 본문 내용 추출
    content_element = soup.find(class_='xe_content')
    if content_element:
        content_text = content_element.get_text(strip=True)
        
        print(f"\n본문 길이: {len(content_text)}자")
        print(f"본문 시작 500자:")
        print(content_text[:500])
        print("...")
        
        # 다양한 절 패턴 찾기
        patterns = [
            r'====(\d+):(\d+)',      # ====31:1
            r'(\d+):(\d+)',          # 31:1
            r'(\d+)장(\d+)절',       # 31장1절
            r'(\d+):(\d+)절',        # 31:1절
            r'====(\d+):(\d+)절',    # ====31:1절
        ]
        
        print(f"\n=== 절 패턴 분석 ===")
        for i, pattern in enumerate(patterns):
            matches = re.findall(pattern, content_text)
            print(f"패턴 {i+1} '{pattern}': {len(matches)}개 매치")
            if matches:
                print(f"  예시: {matches[:5]}")
        
        # 실제 절 구분 찾기
        print(f"\n=== 실제 절 구분 텍스트 ===")
        lines = content_text.split('\n')
        verse_lines = []
        for line in lines:
            if re.search(r'\d+:\d+', line) and len(line) < 50:  # 짧은 줄에서 찾기
                verse_lines.append(line.strip())
        
        print(f"절 구분으로 보이는 줄들 (상위 10개):")
        for line in verse_lines[:10]:
            print(f"  '{line}'")
        
        # 특정 패턴으로 절별 내용 분할 테스트
        if verse_lines:
            test_pattern = r'(\d+):(\d+)'
            verse_matches = list(re.finditer(test_pattern, content_text))
            
            print(f"\n=== 절별 분할 테스트 ===")
            print(f"총 {len(verse_matches)}개 절 발견")
            
            for i, match in enumerate(verse_matches[:3]):  # 처음 3개만
                chapter_num = match.group(1)
                verse_num = match.group(2)
                
                start_pos = match.end()
                if i + 1 < len(verse_matches):
                    end_pos = verse_matches[i + 1].start()
                else:
                    end_pos = start_pos + 200  # 200자만
                
                verse_content = content_text[start_pos:end_pos].strip()
                print(f"\n{chapter_num}:{verse_num}절:")
                print(f"  {verse_content[:150]}...")

if __name__ == "__main__":
    test_verse_pattern() 