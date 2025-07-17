import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import re
from urllib.parse import urljoin, urlparse
import json
from datetime import datetime

class HochmaParser:
    def __init__(self, db_path="hochma_articles.db"):
        """
        호크마 성경주석 파서 초기화
        
        Args:
            db_path (str): SQLite 데이터베이스 파일 경로
        """
        self.base_url = "https://nocr.net"
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session.headers.update(self.headers)
        
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """
        SQLite 데이터베이스 초기화
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 테이블 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id TEXT UNIQUE,
                url TEXT UNIQUE,
                title TEXT,
                content TEXT,
                book_name TEXT,
                chapter TEXT,
                parsed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 인덱스 생성
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_article_id ON articles(article_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_book_name ON articles(book_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chapter ON articles(chapter)')
        
        conn.commit()
        conn.close()
        print(f"데이터베이스 초기화 완료: {self.db_path}")
    
    def fetch_page(self, url, timeout=10):
        """
        웹 페이지 가져오기
        
        Args:
            url (str): 가져올 웹 페이지 URL
            timeout (int): 요청 타임아웃
            
        Returns:
            requests.Response: HTTP 응답 객체
        """
        try:
            if not url.startswith('http'):
                url = urljoin(self.base_url, url)
            
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            response.encoding = 'utf-8'  # 한글 인코딩 설정
            return response
        except requests.RequestException as e:
            print(f"페이지 가져오기 실패 ({url}): {e}")
            return None
    
    def extract_article_data(self, soup, url):
        """
        개별 게시글에서 제목과 본문 추출
        
        Args:
            soup (BeautifulSoup): 파싱된 HTML 객체
            url (str): 게시글 URL
            
        Returns:
            dict: 추출된 게시글 데이터
        """
        article_data = {
            'url': url,
            'title': '',
            'content': '',
            'book_name': '',
            'chapter': '',
            'article_id': ''
        }
        
        # URL에서 게시글 ID 추출
        article_id_match = re.search(r'/(\d+)$', url)
        if article_id_match:
            article_data['article_id'] = article_id_match.group(1)
        
        # 제목 추출 - 호크마 사이트 특화 방식
        # 1. H1 태그 중에서 "호크마 주석, 창세기 XX장" 형식 찾기
        title_found = False
        for h1 in soup.find_all('h1'):
            h1_text = h1.get_text(strip=True)
            if '호크마 주석' in h1_text and ('장' in h1_text or '권' in h1_text or '서' in h1_text):
                article_data['title'] = h1_text
                title_found = True
                break
        
        # 2. 제목이 없으면 title 태그에서 추출
        if not title_found:
            title_tag = soup.find('title')
            if title_tag:
                title_text = title_tag.get_text(strip=True)
                # "호크마 주석, 창세기 01장 - 호크마 주석 - HANGL NOCR" 형식에서 앞부분만 추출
                if ' - ' in title_text:
                    article_data['title'] = title_text.split(' - ')[0]
                else:
                    article_data['title'] = title_text
        
        # 본문 내용 추출 - 호크마 사이트 특화
        content_text = ""
        
        # 1. .xe_content 클래스 (가장 정확한 본문)
        xe_content = soup.find(class_='xe_content')
        if xe_content:
            # 불필요한 태그 제거
            for unwanted in xe_content(['script', 'style', 'nav', 'footer', 'header']):
                unwanted.decompose()
            content_text = xe_content.get_text(strip=True)
        
        # 2. .rd_body 클래스 (대안)
        if not content_text or len(content_text) < 100:
            rd_body = soup.find(class_='rd_body')
            if rd_body:
                for unwanted in rd_body(['script', 'style', 'nav', 'footer', 'header']):
                    unwanted.decompose()
                content_text = rd_body.get_text(strip=True)
        
        # 3. .rhymix_content 클래스 (대안)
        if not content_text or len(content_text) < 100:
            rhymix_content = soup.find(class_='rhymix_content')
            if rhymix_content:
                for unwanted in rhymix_content(['script', 'style', 'nav', 'footer', 'header']):
                    unwanted.decompose()
                content_text = rhymix_content.get_text(strip=True)
        
        # 4. 마지막 수단: 전체 페이지에서 추출 (하지만 노이즈 제거)
        if not content_text or len(content_text) < 50:
            # 불필요한 요소들 제거
            for unwanted in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form']):
                unwanted.decompose()
            
            # 링크 리스트 테이블 제거 (게시글 목록)
            for table in soup.find_all('table'):
                if len(table.find_all('a')) > 10:  # 링크가 많은 테이블은 목록으로 간주
                    table.decompose()
            
            content_text = soup.get_text(strip=True)
        
        article_data['content'] = content_text
        
        # 성경책 이름과 장 정보 추출 (제목에서)
        if article_data['title']:
            # "호크마 주석, 창세기 30장" 형식에서 추출
            book_chapter_match = re.search(r'호크마 주석,\s*([가-힣]+)\s*(\d+)장', article_data['title'])
            if book_chapter_match:
                article_data['book_name'] = book_chapter_match.group(1)
                article_data['chapter'] = book_chapter_match.group(2)
            else:
                # 일반적인 형식 시도
                general_match = re.search(r'([가-힣]+)\s*(\d+)장', article_data['title'])
                if general_match:
                    article_data['book_name'] = general_match.group(1)
                    article_data['chapter'] = general_match.group(2)
                else:
                    # "호크마 주석, 요한복음" 같은 형식도 시도
                    book_only_match = re.search(r'호크마 주석,\s*([가-힣]+)', article_data['title'])
                    if book_only_match:
                        article_data['book_name'] = book_only_match.group(1)
        
        return article_data
    
    def save_article_to_db(self, article_data):
        """
        게시글 데이터를 데이터베이스에 저장
        
        Args:
            article_data (dict): 게시글 데이터
            
        Returns:
            bool: 저장 성공 여부
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO articles 
                (article_id, url, title, content, book_name, chapter, parsed_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                article_data['article_id'],
                article_data['url'],
                article_data['title'],
                article_data['content'],
                article_data['book_name'],
                article_data['chapter'],
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"데이터베이스 저장 실패: {e}")
            return False
    
    def parse_single_article(self, article_id):
        """
        단일 게시글 파싱
        
        Args:
            article_id (str): 게시글 ID
            
        Returns:
            dict: 파싱된 게시글 데이터
        """
        url = f"{self.base_url}/com_kor_hochma/{article_id}"
        
        print(f"게시글 파싱 중: {url}")
        
        response = self.fetch_page(url)
        if not response:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        article_data = self.extract_article_data(soup, url)
        
        if article_data['title'] and article_data['content']:
            if self.save_article_to_db(article_data):
                print(f"✓ 저장 완료: {article_data['title'][:50]}...")
                return article_data
            else:
                print(f"✗ 저장 실패: {article_data['title'][:50]}...")
        else:
            print(f"✗ 데이터 추출 실패: {url}")
        
        return article_data
    
    def parse_article_range(self, start_id, end_id, delay=1):
        """
        범위 내의 게시글들을 순차적으로 파싱
        
        Args:
            start_id (int): 시작 게시글 ID
            end_id (int): 종료 게시글 ID
            delay (float): 요청 간 지연 시간 (초)
            
        Returns:
            list: 파싱된 게시글 데이터 리스트
        """
        parsed_articles = []
        
        print(f"게시글 범위 파싱 시작: {start_id} ~ {end_id}")
        
        for article_id in range(start_id, end_id + 1):
            article_data = self.parse_single_article(str(article_id))
            
            if article_data:
                parsed_articles.append(article_data)
            
            # 요청 간 지연
            if delay > 0:
                time.sleep(delay)
        
        print(f"파싱 완료: 총 {len(parsed_articles)}개 게시글")
        return parsed_articles
    
    def get_articles_from_db(self, book_name=None, limit=None):
        """
        데이터베이스에서 게시글 조회
        
        Args:
            book_name (str): 성경책 이름으로 필터링 (선택사항)
            limit (int): 조회할 최대 개수 (선택사항)
            
        Returns:
            list: 게시글 데이터 리스트
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM articles"
        params = []
        
        if book_name:
            query += " WHERE book_name = ?"
            params.append(book_name)
        
        query += " ORDER BY article_id DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        articles = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return articles
    
    def export_to_json(self, filename, book_name=None):
        """
        데이터베이스 내용을 JSON 파일로 내보내기
        
        Args:
            filename (str): 저장할 파일명
            book_name (str): 성경책 이름으로 필터링 (선택사항)
        """
        articles = self.get_articles_from_db(book_name=book_name)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"JSON 내보내기 완료: {filename} ({len(articles)}개 게시글)")
    
    def get_statistics(self):
        """
        데이터베이스 통계 정보 반환
        
        Returns:
            dict: 통계 정보
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 전체 게시글 수
        cursor.execute("SELECT COUNT(*) FROM articles")
        total_count = cursor.fetchone()[0]
        
        # 성경책별 게시글 수
        cursor.execute("""
            SELECT book_name, COUNT(*) as count 
            FROM articles 
            WHERE book_name != '' 
            GROUP BY book_name 
            ORDER BY count DESC
        """)
        book_stats = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_articles': total_count,
            'books': dict(book_stats)
        }


def main():
    """
    메인 함수 - 사용 예제
    """
    parser = HochmaParser()
    
    print("호크마 성경주석 파서")
    print("=" * 50)
    
    while True:
        print("\n선택할 작업:")
        print("1. 단일 게시글 파싱")
        print("2. 범위 게시글 파싱")
        print("3. 데이터베이스 조회")
        print("4. JSON 내보내기")
        print("5. 통계 보기")
        print("6. 종료")
        
        choice = input("\n선택 (1-6): ").strip()
        
        if choice == '1':
            article_id = input("게시글 ID를 입력하세요: ").strip()
            if article_id:
                parser.parse_single_article(article_id)
        
        elif choice == '2':
            try:
                start_id = int(input("시작 ID: "))
                end_id = int(input("종료 ID: "))
                delay = float(input("지연 시간(초, 기본 1초): ") or "1")
                
                parser.parse_article_range(start_id, end_id, delay)
            except ValueError:
                print("올바른 숫자를 입력해주세요.")
        
        elif choice == '3':
            book_name = input("성경책 이름 (전체 조회시 엔터): ").strip() or None
            limit = input("조회 개수 제한 (전체 조회시 엔터): ").strip()
            limit = int(limit) if limit else None
            
            articles = parser.get_articles_from_db(book_name=book_name, limit=limit)
            
            print(f"\n조회 결과: {len(articles)}개")
            for article in articles[:5]:  # 상위 5개만 표시
                print(f"- [{article['article_id']}] {article['title'][:50]}...")
            
            if len(articles) > 5:
                print(f"... 및 {len(articles) - 5}개 더")
        
        elif choice == '4':
            filename = input("저장할 파일명 (.json): ").strip()
            if not filename.endswith('.json'):
                filename += '.json'
            
            book_name = input("성경책 이름 (전체 내보내기시 엔터): ").strip() or None
            parser.export_to_json(filename, book_name=book_name)
        
        elif choice == '5':
            stats = parser.get_statistics()
            print(f"\n=== 통계 정보 ===")
            print(f"총 게시글 수: {stats['total_articles']}")
            print(f"\n성경책별 게시글 수:")
            for book, count in list(stats['books'].items())[:10]:
                print(f"  {book}: {count}개")
            
            if len(stats['books']) > 10:
                print(f"  ... 및 {len(stats['books']) - 10}개 성경책 더")
        
        elif choice == '6':
            print("프로그램을 종료합니다.")
            break
        
        else:
            print("올바른 선택지를 입력해주세요.")


if __name__ == "__main__":
    main() 