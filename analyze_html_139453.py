import requests
from bs4 import BeautifulSoup
import re

def analyze_html_139453():
    """139453 게시글의 HTML 구조 분석"""
    
    url = "https://nocr.net/com_kor_hochma/139453"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"🔍 {url} HTML 구조 분석 중...")
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        content_element = soup.find(class_='xe_content') or soup.find(class_='rd_body') or soup.find(class_='rhymix_content')
        
        if content_element:
            print(f"📄 HTML 구조:")
            print(f"  - 태그명: {content_element.name}")
            print(f"  - 클래스: {content_element.get('class', [])}")
            
            # 원본 HTML 텍스트 일부 확인
            html_content = str(content_element)
            print(f"\n📝 원본 HTML (처음 500자):")
            print(html_content[:500] + "...")
            
            # 다양한 방법으로 텍스트 추출 시도
            print(f"\n🔄 다양한 텍스트 추출 방법:")
            
            # 방법 1: get_text() with strip=True (기본)
            text1 = content_element.get_text(strip=True)
            lines1 = text1.split('\n')
            print(f"1. get_text(strip=True): {len(lines1)}줄")
            print(f"   처음 100자: {text1[:100]}...")
            
            # 방법 2: get_text() with strip=False
            text2 = content_element.get_text(strip=False)
            lines2 = text2.split('\n')
            print(f"2. get_text(strip=False): {len(lines2)}줄")
            print(f"   처음 100자: {text2[:100]}...")
            
            # 방법 3: get_text() with separator='\n'
            text3 = content_element.get_text(separator='\n', strip=True)
            lines3 = text3.split('\n')
            print(f"3. get_text(separator='\\n'): {len(lines3)}줄")
            print(f"   처음 100자: {text3[:100]}...")
            
            # 방법 4: 원본에서 <br> 태그 확인
            br_count = len(content_element.find_all('br'))
            p_count = len(content_element.find_all('p'))
            div_count = len(content_element.find_all('div'))
            print(f"4. HTML 태그 개수: <br>={br_count}, <p>={p_count}, <div>={div_count}")
            
            # 방법 5: <br> 태그를 줄바꿈으로 변환 후 텍스트 추출
            # <br> 태그를 \n으로 변환
            for br in content_element.find_all('br'):
                br.replace_with('\n')
            
            text5 = content_element.get_text()
            lines5 = [line.strip() for line in text5.split('\n') if line.strip()]
            print(f"5. <br> 변환 후: {len(lines5)}줄")
            
            # 처음 20줄 표시
            print(f"\n📋 <br> 변환 후 처음 20줄:")
            for i, line in enumerate(lines5[:20]):
                # 절 구분자 패턴 확인
                patterns = [
                    r'^(\d+):(\d+)$',                      # 19:11
                    r'^(\d+):(\d+(?:,\d+)+)$',             # 19:23,24
                    r'^(\d+):(\d+)-(\d+)$',                # 19:10-14
                ]
                
                is_separator = False
                for pattern in patterns:
                    if re.match(pattern, line):
                        is_separator = True
                        break
                
                status = "✅ 절구분자" if is_separator else "📝 내용"
                print(f"  [{i+1:2}] {status} | '{line[:60]}{'...' if len(line) > 60 else ''}'")
            
            # 절 구분자 찾기
            verse_separators = []
            for i, line in enumerate(lines5):
                for pattern in patterns:
                    match = re.match(pattern, line)
                    if match:
                        verse_separators.append((i, line, match.groups()))
                        break
            
            print(f"\n📊 발견된 절 구분자: {len(verse_separators)}개")
            for i, (line_idx, line_text, groups) in enumerate(verse_separators[:10]):  # 처음 10개만
                print(f"  [{i+1}] 줄 {line_idx+1}: '{line_text}' -> {groups}")
                
    except Exception as e:
        print(f"❌ 분석 실패: {e}")

if __name__ == "__main__":
    analyze_html_139453() 