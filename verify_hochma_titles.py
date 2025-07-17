import requests
from bs4 import BeautifulSoup
import re

def get_actual_title(article_id):
    """실제 게시글의 제목을 가져오는 함수"""
    url = f"https://nocr.net/index.php?mid=com_kor_hochma&document_srl={article_id}"
    
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 다양한 제목 추출 방법 시도
            title_methods = [
                # H1 태그
                lambda s: s.find('h1'),
                # title 태그
                lambda s: s.find('title'),
                # .xe-content-header 클래스
                lambda s: s.find('div', class_='xe-content-header'),
                # .document_title 클래스
                lambda s: s.find('div', class_='document_title'),
                # .title 클래스
                lambda s: s.find('div', class_='title'),
                # h2 태그
                lambda s: s.find('h2'),
                # meta title
                lambda s: s.find('meta', {'property': 'og:title'}),
            ]
            
            print(f"\n📄 게시글 {article_id} 제목 추출 시도:")
            
            for i, method in enumerate(title_methods):
                try:
                    element = method(soup)
                    if element:
                        if element.name == 'meta':
                            title_text = element.get('content', '').strip()
                        else:
                            title_text = element.get_text(strip=True)
                        
                        if title_text and len(title_text) > 5:  # 최소 길이 확인
                            print(f"  방법 {i+1}: {title_text}")
                        else:
                            print(f"  방법 {i+1}: (짧은 텍스트) {title_text}")
                    else:
                        print(f"  방법 {i+1}: 요소 없음")
                except Exception as e:
                    print(f"  방법 {i+1}: 오류 - {e}")
            
            # HTML 구조 일부 출력
            print(f"\n🔍 HTML 구조 샘플:")
            head = soup.find('head')
            if head:
                title_tag = head.find('title')
                if title_tag:
                    print(f"  <title>: {title_tag.get_text(strip=True)}")
            
            # 본문에서 호크마 주석 패턴 찾기
            content_area = soup.find('div', class_='xe_content') or soup.find('div', class_='rd_body')
            if content_area:
                content_text = content_area.get_text()
                hochma_pattern = r'호크마 주석[,\s]*([가-힣]+(?:상|하)?(?:전서|후서)?(?:일서|이서|삼서)?(?:복음)?(?:기)?(?:애가)?)\s*(\d+)장'
                match = re.search(hochma_pattern, content_text)
                if match:
                    book_name = match.group(1)
                    chapter = match.group(2)
                    print(f"  본문에서 발견: 호크마 주석, {book_name} {chapter}장")
                    return f"호크마 주석, {book_name} {chapter}장"
            
            return None
            
    except Exception as e:
        print(f"❌ 게시글 {article_id} 접근 실패: {e}")
        return None

def test_multiple_articles():
    """여러 게시글의 제목 확인"""
    test_articles = [139393, 139394, 139395, 139400, 139450, 139500, 140000, 141000]
    
    print("🔍 여러 게시글의 실제 제목 확인")
    print("=" * 50)
    
    results = {}
    
    for article_id in test_articles:
        print(f"\n📋 게시글 ID: {article_id}")
        title = get_actual_title(article_id)
        results[article_id] = title
        
        if title:
            # 성경책명과 장 추출
            pattern = r'호크마 주석[,\s]*([가-힣]+(?:상|하)?(?:전서|후서)?(?:일서|이서|삼서)?(?:복음)?(?:기)?(?:애가)?)\s*(\d+)장'
            match = re.search(pattern, title)
            if match:
                book_name = match.group(1)
                chapter = match.group(2)
                print(f"  ✅ 추출 성공: {book_name} {chapter}장")
            else:
                print(f"  ⚠️  패턴 매치 실패: {title}")
        else:
            print(f"  ❌ 제목 추출 실패")
    
    return results

def main():
    """메인 함수"""
    results = test_multiple_articles()
    
    print(f"\n📊 결과 요약:")
    success_count = sum(1 for title in results.values() if title)
    print(f"  성공: {success_count}/{len(results)}")
    
    if success_count > 0:
        print(f"\n✅ 성공한 제목들:")
        for article_id, title in results.items():
            if title:
                print(f"  {article_id}: {title}")

if __name__ == "__main__":
    main() 