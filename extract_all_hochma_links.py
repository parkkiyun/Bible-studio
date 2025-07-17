import requests
from bs4 import BeautifulSoup
import re
import json
import time
from datetime import datetime
import pandas as pd

class HochmaLinkExtractor:
    def __init__(self):
        self.base_url = "https://nocr.net/com_kor_hochma"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def extract_links_from_page(self, page_num=1):
        """특정 페이지에서 모든 게시글 링크 추출"""
        if page_num == 1:
            url = self.base_url
        else:
            url = f"{self.base_url}?page={page_num}"
        
        print(f"📄 페이지 {page_num} 스캔 중: {url}")
        
        try:
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                print(f"❌ 페이지 {page_num} 접근 실패: {response.status_code}")
                return [], False
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 게시글 링크 찾기 - 다양한 패턴 시도
            links = []
            
            # 패턴 1: /com_kor_hochma/숫자 형태의 링크
            pattern1_links = soup.find_all('a', href=re.compile(r'/com_kor_hochma/(\d+)'))
            for link in pattern1_links:
                href = link.get('href')
                match = re.search(r'/com_kor_hochma/(\d+)', href)
                if match:
                    article_id = int(match.group(1))
                    title = link.get_text(strip=True)
                    links.append({
                        'article_id': article_id,
                        'title': title,
                        'href': href,
                        'page': page_num
                    })
            
            # 패턴 2: document_srl= 파라미터가 있는 링크
            pattern2_links = soup.find_all('a', href=re.compile(r'document_srl=(\d+)'))
            for link in pattern2_links:
                href = link.get('href')
                match = re.search(r'document_srl=(\d+)', href)
                if match:
                    article_id = int(match.group(1))
                    title = link.get_text(strip=True)
                    # 중복 제거
                    if not any(l['article_id'] == article_id for l in links):
                        links.append({
                            'article_id': article_id,
                            'title': title,
                            'href': href,
                            'page': page_num
                        })
            
            # 호크마 주석 패턴이 있는 링크만 필터링
            filtered_links = []
            for link in links:
                if '호크마 주석' in link['title']:
                    filtered_links.append(link)
            
            print(f"  발견된 링크: {len(links)}개, 호크마 주석: {len(filtered_links)}개")
            
            # 다음 페이지 존재 확인
            has_next = self.check_next_page_exists(soup, page_num)
            
            return filtered_links, has_next
            
        except Exception as e:
            print(f"❌ 페이지 {page_num} 처리 중 오류: {e}")
            return [], False
    
    def check_next_page_exists(self, soup, current_page):
        """다음 페이지가 존재하는지 확인"""
        try:
            # 페이지네이션 영역 찾기
            pagination = soup.find('div', class_='pagination') or soup.find('div', class_='paging')
            
            if pagination:
                # "Next" 버튼이나 다음 페이지 번호 링크 찾기
                next_links = pagination.find_all('a', href=re.compile(f'page={current_page + 1}'))
                if next_links:
                    return True
                
                # 또는 숫자로 된 페이지 링크 확인
                page_links = pagination.find_all('a', href=re.compile(r'page=(\d+)'))
                max_page = 0
                for link in page_links:
                    match = re.search(r'page=(\d+)', link.get('href', ''))
                    if match:
                        page_num = int(match.group(1))
                        max_page = max(max_page, page_num)
                
                return current_page < max_page
            
            # 테이블 기반 목록에서 행 수 확인 (페이지당 보통 50개)
            table_rows = soup.find_all('tr')
            article_rows = [row for row in table_rows if row.find('a', href=re.compile(r'com_kor_hochma'))]
            
            # 50개 행이 있으면 다음 페이지가 있을 가능성
            return len(article_rows) >= 50
            
        except Exception as e:
            print(f"⚠️ 다음 페이지 확인 실패: {e}")
            return False
    
    def extract_all_links(self, max_pages=100):
        """모든 페이지에서 링크 추출"""
        print("🔍 호크마 사이트 모든 게시글 링크 추출 시작")
        print("=" * 60)
        
        all_links = []
        page_num = 1
        
        while page_num <= max_pages:
            links, has_next = self.extract_links_from_page(page_num)
            
            if links:
                all_links.extend(links)
                print(f"  ✅ 페이지 {page_num}: {len(links)}개 링크 추가")
            else:
                print(f"  ⚠️ 페이지 {page_num}: 링크 없음")
            
            if not has_next:
                print(f"  🏁 페이지 {page_num}에서 종료 (더 이상 페이지 없음)")
                break
            
            page_num += 1
            time.sleep(0.5)  # 요청 간격
        
        # 중복 제거 (article_id 기준)
        unique_links = {}
        for link in all_links:
            article_id = link['article_id']
            if article_id not in unique_links:
                unique_links[article_id] = link
        
        unique_links_list = list(unique_links.values())
        unique_links_list.sort(key=lambda x: x['article_id'])
        
        print(f"\n📊 추출 결과:")
        print(f"  총 스캔 페이지: {page_num - 1}")
        print(f"  발견된 전체 링크: {len(all_links)}")
        print(f"  중복 제거 후: {len(unique_links_list)}")
        print(f"  article_id 범위: {min(unique_links_list, key=lambda x: x['article_id'])['article_id']} ~ {max(unique_links_list, key=lambda x: x['article_id'])['article_id']}")
        
        return unique_links_list
    
    def analyze_extracted_links(self, links):
        """추출된 링크들 분석"""
        print(f"\n📊 추출된 링크 분석")
        print("=" * 40)
        
        # 성경책별 분류
        book_articles = {}
        unmatched_titles = []
        
        for link in links:
            title = link['title']
            
            # 호크마 주석 패턴에서 성경책명과 장 추출
            pattern = r'호크마 주석[,\s]*([가-힣]+(?:상|하)?(?:전서|후서)?(?:일서|이서|삼서)?(?:복음)?(?:기)?(?:애가)?)\s*(\d+)장'
            match = re.search(pattern, title)
            
            if match:
                book_name = match.group(1)
                chapter = int(match.group(2))
                
                if book_name not in book_articles:
                    book_articles[book_name] = []
                
                book_articles[book_name].append({
                    'article_id': link['article_id'],
                    'chapter': chapter,
                    'title': title
                })
            else:
                unmatched_titles.append(title)
        
        print(f"📚 성경책별 통계:")
        for book_name in sorted(book_articles.keys()):
            chapters = sorted([item['chapter'] for item in book_articles[book_name]])
            article_count = len(book_articles[book_name])
            min_chapter = min(chapters)
            max_chapter = max(chapters)
            
            print(f"  {book_name}: {article_count}개 ({min_chapter}~{max_chapter}장)")
        
        if unmatched_titles:
            print(f"\n⚠️ 패턴 매치 안된 제목들 ({len(unmatched_titles)}개):")
            for title in unmatched_titles[:10]:  # 처음 10개만 출력
                print(f"  - {title}")
        
        return book_articles
    
    def save_results(self, links, book_articles):
        """결과 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. 전체 링크 목록 저장
        links_df = pd.DataFrame(links)
        links_filename = f"hochma_all_links_{timestamp}.xlsx"
        links_df.to_excel(links_filename, index=False)
        
        # 2. 성경책별 정리된 데이터 저장
        organized_data = []
        for book_name, articles in book_articles.items():
            for article in articles:
                organized_data.append({
                    'book_name': book_name,
                    'chapter': article['chapter'],
                    'article_id': article['article_id'],
                    'title': article['title']
                })
        
        organized_df = pd.DataFrame(organized_data)
        organized_df = organized_df.sort_values(['book_name', 'chapter'])
        organized_filename = f"hochma_organized_links_{timestamp}.xlsx"
        organized_df.to_excel(organized_filename, index=False)
        
        # 3. JSON 형태로도 저장
        json_data = {
            'extraction_timestamp': timestamp,
            'total_links': len(links),
            'total_books': len(book_articles),
            'links': links,
            'organized_by_book': book_articles
        }
        
        json_filename = f"hochma_all_links_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 결과 저장:")
        print(f"  전체 링크: {links_filename}")
        print(f"  정리된 데이터: {organized_filename}")
        print(f"  JSON 데이터: {json_filename}")
        
        return links_filename, organized_filename, json_filename

def main():
    """메인 함수"""
    print("🔗 호크마 사이트 모든 게시글 링크 추출")
    print("=" * 50)
    
    extractor = HochmaLinkExtractor()
    
    # 1단계: 모든 링크 추출
    links = extractor.extract_all_links(max_pages=50)  # 최대 50페이지까지
    
    if not links:
        print("❌ 링크를 찾을 수 없습니다.")
        return
    
    # 2단계: 추출된 링크 분석
    book_articles = extractor.analyze_extracted_links(links)
    
    # 3단계: 결과 저장
    links_file, organized_file, json_file = extractor.save_results(links, book_articles)
    
    print(f"\n✅ 링크 추출 완료!")
    print(f"  발견된 게시글: {len(links)}개")
    print(f"  발견된 성경책: {len(book_articles)}개")
    
    # 4단계: Bible Database와 비교
    print(f"\n📖 완성도 예상:")
    expected_total = 1189  # 사이트에서 표시된 총 게시글 수
    actual_found = len(links)
    completion_rate = (actual_found / expected_total) * 100
    
    print(f"  예상 총 게시글: {expected_total}개")
    print(f"  실제 발견: {actual_found}개")
    print(f"  완성도: {completion_rate:.1f}%")

if __name__ == "__main__":
    main() 