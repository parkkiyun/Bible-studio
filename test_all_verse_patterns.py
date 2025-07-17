import requests
from bs4 import BeautifulSoup
import re

def test_all_verse_patterns():
    """
    호크마 사이트에서 모든 절 구분 패턴 분석
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
    
    # 본문 내용 추출
    content_element = soup.find(class_='xe_content')
    if content_element:
        content_text = content_element.get_text(strip=True)
        
        print(f"본문 길이: {len(content_text)}자")
        
        # 다양한 등호 패턴 찾기
        patterns = [
            r'====(\d+):(\d+)',     # 4개 등호
            r'===(\d+):(\d+)',      # 3개 등호  
            r'==(\d+):(\d+)',       # 2개 등호
            r'=(\d+):(\d+)',        # 1개 등호
            r'={3,}(\d+):(\d+)',    # 3개 이상 등호
            r'={2,}(\d+):(\d+)',    # 2개 이상 등호
        ]
        
        print(f"\n=== 등호 패턴 분석 ===")
        for i, pattern in enumerate(patterns):
            matches = re.findall(pattern, content_text)
            print(f"패턴 {i+1} '{pattern}': {len(matches)}개 매치")
            if matches:
                print(f"  예시: {matches[:5]}")
        
        # 실제 등호로 시작하는 모든 줄 찾기
        print(f"\n=== 등호로 시작하는 모든 줄 ===")
        lines = content_text.split('\n')
        equal_lines = []
        for line in lines:
            line = line.strip()
            if re.match(r'^=+\d+:\d+', line):
                equal_lines.append(line)
        
        print(f"등호로 시작하는 줄 수: {len(equal_lines)}개")
        print("모든 등호 줄들:")
        for line in equal_lines:
            # 등호 개수 세기
            equal_count = len(re.match(r'^=+', line).group())
            print(f"  {equal_count}개 등호: {line[:50]}")
        
        # 최적 패턴 제안
        print(f"\n=== 최적 패턴 제안 ===")
        # 3개 이상 등호 패턴으로 모든 절 찾기
        optimal_pattern = r'={3,}(\d+):(\d+)'
        all_verses = re.findall(optimal_pattern, content_text)
        print(f"최적 패턴 '{optimal_pattern}': {len(all_verses)}개 절 발견")
        
        if all_verses:
            print("발견된 모든 절:")
            for chapter, verse in all_verses:
                print(f"  {chapter}:{verse}")

if __name__ == "__main__":
    test_all_verse_patterns() 