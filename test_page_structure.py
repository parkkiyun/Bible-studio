import requests
from bs4 import BeautifulSoup
import re

def analyze_page_structure(url):
    """
    페이지 구조 분석
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print(f"페이지 분석: {url}")
    print("=" * 60)
    
    # 타이틀 태그
    title = soup.find('title')
    if title:
        print(f"Title 태그: {title.get_text()}")
    
    # 모든 h1, h2, h3 태그
    print("\n=== 헤딩 태그들 ===")
    for i, heading in enumerate(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])):
        print(f"H{heading.name[1:]} [{i}]: {heading.get_text(strip=True)[:100]}")
    
    # 클래스 이름들 조사
    print("\n=== 주요 클래스들 ===")
    class_names = set()
    for element in soup.find_all():
        if element.get('class'):
            for cls in element.get('class'):
                class_names.add(cls)
    
    important_classes = [cls for cls in class_names if any(keyword in cls.lower() 
                        for keyword in ['title', 'content', 'article', 'post', 'text', 
                                      'subject', 'body', 'main'])]
    
    for cls in sorted(important_classes):
        elements = soup.find_all(class_=cls)
        if elements:
            print(f".{cls} ({len(elements)}개): {elements[0].get_text(strip=True)[:80]}...")
    
    # ID들 조사
    print("\n=== 주요 ID들 ===")
    ids = set()
    for element in soup.find_all():
        if element.get('id'):
            ids.add(element.get('id'))
    
    important_ids = [id_name for id_name in ids if any(keyword in id_name.lower() 
                    for keyword in ['title', 'content', 'article', 'post', 'text', 
                                  'subject', 'body', 'main'])]
    
    for id_name in sorted(important_ids):
        element = soup.find(id=id_name)
        if element:
            print(f"#{id_name}: {element.get_text(strip=True)[:80]}...")
    
    # 테이블 구조 확인
    print("\n=== 테이블 구조 ===")
    tables = soup.find_all('table')
    for i, table in enumerate(tables[:3]):  # 상위 3개 테이블만
        print(f"Table {i}: {len(table.find_all('tr'))}행, {len(table.find_all('td'))}셀")
        # 첫 번째 몇 개 셀의 내용 확인
        cells = table.find_all(['td', 'th'])[:5]
        for j, cell in enumerate(cells):
            cell_text = cell.get_text(strip=True)
            if len(cell_text) > 20:
                print(f"  셀 {j}: {cell_text[:50]}...")
    
    return soup

if __name__ == "__main__":
    # 테스트할 URL들
    test_urls = [
        "https://nocr.net/com_kor_hochma/139393",
        "https://nocr.net/com_kor_hochma/139475"  # 창세기 30장
    ]
    
    for url in test_urls:
        try:
            analyze_page_structure(url)
            print("\n" + "="*80 + "\n")
        except Exception as e:
            print(f"오류 발생 ({url}): {e}")
            print("\n" + "="*80 + "\n") 