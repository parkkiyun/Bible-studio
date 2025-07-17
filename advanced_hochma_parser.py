import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import re
from urllib.parse import urljoin
import json
from datetime import datetime

class AdvancedHochmaParser:
    def __init__(self, db_path="bible_database.db"):
        """
        고급 호크마 성경주석 파서 초기화
        기존 bible_database.db와 호환되는 구조로 주석 데이터 저장
        
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
        self.init_commentary_table()
    
    def init_commentary_table(self):
        """
        기존 bible_database.db에 주석 테이블 추가
        verses 테이블과 동일한 구조 유지
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # commentaries 테이블 생성 (verses 테이블과 동일한 구조)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS commentaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_name TEXT NOT NULL,
                book_code INTEGER NOT NULL,
                chapter INTEGER NOT NULL,
                verse INTEGER NOT NULL,
                text TEXT NOT NULL,
                version TEXT NOT NULL,
                verse_title TEXT,
                commentary_name TEXT NOT NULL,
                original_url TEXT,
                parsed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 인덱스 생성
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_commentaries_book ON commentaries(book_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_commentaries_chapter ON commentaries(book_name, chapter)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_commentaries_verse ON commentaries(book_name, chapter, verse)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_commentaries_version ON commentaries(version)')
        
        conn.commit()
        conn.close()
        print(f"주석 테이블 초기화 완료: {self.db_path}")
    
    def get_book_code(self, book_name):
        """
        성경책 이름으로부터 book_code 조회
        기존 verses 테이블에서 매핑 정보 가져오기
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT book_code FROM verses WHERE book_name = ? LIMIT 1", (book_name,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0]
        else:
            # 기본 매핑 (성경책 순서)
            book_mapping = {
                '창세기': 1, '출애굽기': 2, '레위기': 3, '민수기': 4, '신명기': 5,
                '여호수아': 6, '사사기': 7, '룻기': 8, '사무엘상': 9, '사무엘하': 10,
                '열왕기상': 11, '열왕기하': 12, '역대상': 13, '역대하': 14, '에스라': 15,
                '느헤미야': 16, '에스더': 17, '욥기': 18, '시편': 19, '잠언': 20,
                '전도서': 21, '아가': 22, '이사야': 23, '예레미야': 24, '예레미야애가': 25,
                '에스겔': 26, '다니엘': 27, '호세아': 28, '요엘': 29, '아모스': 30,
                '오바댜': 31, '요나': 32, '미가': 33, '나훔': 34, '하박국': 35,
                '스바냐': 36, '학개': 37, '스가랴': 38, '말라기': 39,
                '마태복음': 40, '마가복음': 41, '누가복음': 42, '요한복음': 43, '사도행전': 44,
                '로마서': 45, '고린도전서': 46, '고린도후서': 47, '갈라디아서': 48, '에베소서': 49,
                '빌립보서': 50, '골로새서': 51, '데살로니가전서': 52, '데살로니가후서': 53,
                '디모데전서': 54, '디모데후서': 55, '디도서': 56, '빌레몬서': 57,
                '히브리서': 58, '야고보서': 59, '베드로전서': 60, '베드로후서': 61,
                '요한일서': 62, '요한이서': 63, '요한삼서': 64, '유다서': 65, '요한계시록': 66
            }
            return book_mapping.get(book_name, 999)  # 기본값 999
    
    def fetch_page(self, url, timeout=10):
        """
        웹 페이지 가져오기
        """
        try:
            if not url.startswith('http'):
                url = urljoin(self.base_url, url)
            
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response
        except requests.RequestException as e:
            print(f"페이지 가져오기 실패 ({url}): {e}")
            return None
    
    def extract_detailed_commentary(self, soup, url):
        """
        상세한 주석 데이터 추출
        
        Args:
            soup (BeautifulSoup): 파싱된 HTML 객체
            url (str): 게시글 URL
            
        Returns:
            dict: 추출된 주석 데이터 (절별로 구분)
        """
        article_data = {
            'url': url,
            'title': '',
            'commentary_name': '',
            'book_name': '',
            'chapter': '',
            'verse_commentaries': []  # 절별 주석 리스트
        }
        
        # 1. 제목에서 주석명과 성경책 정보 추출
        title_found = False
        for h1 in soup.find_all('h1'):
            h1_text = h1.get_text(strip=True)
            if '주석' in h1_text and ('장' in h1_text or '권' in h1_text or '서' in h1_text):
                article_data['title'] = h1_text
                title_found = True
                break
        
        if not title_found:
            title_tag = soup.find('title')
            if title_tag:
                title_text = title_tag.get_text(strip=True)
                if ' - ' in title_text:
                    article_data['title'] = title_text.split(' - ')[0]
                else:
                    article_data['title'] = title_text
        
        # 2. 제목에서 주석명과 성경책 정보 파싱
        if article_data['title']:
            # "호크마 주석, 창세기 31장" 형식 파싱
            title_match = re.search(r'([^,]+),\s*([가-힣]+)\s*(\d+)장', article_data['title'])
            if title_match:
                article_data['commentary_name'] = title_match.group(1).strip()
                article_data['book_name'] = title_match.group(2).strip()
                article_data['chapter'] = title_match.group(3).strip()
        
        # 3. 본문에서 절별 주석 추출
        content_element = soup.find(class_='xe_content') or soup.find(class_='rd_body') or soup.find(class_='rhymix_content')
        
        if content_element:
            # HTML 텍스트 전체 가져오기
            content_text = content_element.get_text(strip=True)
            
            # ====31:1 또는 ===31:1 형식의 절 구분자 찾기 (3개 이상 등호)
            verse_pattern = r'={3,}(\d+):(\d+)'
            verse_matches = list(re.finditer(verse_pattern, content_text))
            
            if verse_matches:
                for i, match in enumerate(verse_matches):
                    chapter_num = match.group(1)
                    verse_num = match.group(2)
                    
                    # 현재 절의 시작 위치
                    start_pos = match.end()
                    
                    # 다음 절의 시작 위치 (또는 텍스트 끝)
                    if i + 1 < len(verse_matches):
                        end_pos = verse_matches[i + 1].start()
                    else:
                        end_pos = len(content_text)
                    
                    # 절 주석 내용 추출
                    verse_commentary = content_text[start_pos:end_pos].strip()
                    
                    # 절 주석 정리 (불필요한 텍스트 제거)
                    verse_commentary = re.sub(r'^절[^가-힣]*', '', verse_commentary)  # "절"로 시작하는 부분 제거
                    verse_commentary = verse_commentary.strip()
                    
                    if verse_commentary and len(verse_commentary) > 10:  # 최소 길이 체크
                        article_data['verse_commentaries'].append({
                            'chapter': int(chapter_num),
                            'verse': int(verse_num),
                            'commentary': verse_commentary
                        })
            
            # 절 구분자가 없는 경우 전체 텍스트를 하나의 주석으로 처리
            if not article_data['verse_commentaries'] and len(content_text) > 100:
                # 제목에서 장 정보가 있다면 해당 장의 1절로 저장
                if article_data['chapter']:
                    article_data['verse_commentaries'].append({
                        'chapter': int(article_data['chapter']),
                        'verse': 1,
                        'commentary': content_text
                    })
        
        return article_data
    
    def save_commentary_to_db(self, article_data):
        """
        절별 주석 데이터를 데이터베이스에 저장
        """
        if not article_data['verse_commentaries']:
            print("저장할 주석 데이터가 없습니다.")
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            book_code = self.get_book_code(article_data['book_name'])
            version = f"{article_data['commentary_name']}-commentary"
            
            saved_count = 0
            for verse_data in article_data['verse_commentaries']:
                cursor.execute('''
                    INSERT OR REPLACE INTO commentaries 
                    (book_name, book_code, chapter, verse, text, version, verse_title, 
                     commentary_name, original_url, parsed_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    article_data['book_name'],
                    book_code,
                    verse_data['chapter'],
                    verse_data['verse'],
                    verse_data['commentary'],
                    version,
                    None,  # verse_title
                    article_data['commentary_name'],
                    article_data['url'],
                    datetime.now()
                ))
                saved_count += 1
            
            conn.commit()
            conn.close()
            
            print(f"✓ 저장 완료: {article_data['book_name']} {article_data['chapter']}장 ({saved_count}개 절)")
            return True
            
        except sqlite3.Error as e:
            print(f"데이터베이스 저장 실패: {e}")
            return False
    
    def parse_single_article(self, article_id):
        """
        단일 게시글 상세 파싱
        """
        url = f"{self.base_url}/com_kor_hochma/{article_id}"
        
        print(f"상세 파싱 중: {url}")
        
        response = self.fetch_page(url)
        if not response:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        article_data = self.extract_detailed_commentary(soup, url)
        
        if article_data['verse_commentaries']:
            if self.save_commentary_to_db(article_data):
                return article_data
            else:
                print(f"✗ 저장 실패: {article_data['title']}")
        else:
            print(f"✗ 주석 데이터 추출 실패: {url}")
        
        return article_data
    
    def parse_article_range(self, start_id, end_id, delay=1):
        """
        범위 내의 게시글들을 순차적으로 상세 파싱
        """
        parsed_articles = []
        
        print(f"상세 파싱 시작: {start_id} ~ {end_id}")
        
        for article_id in range(start_id, end_id + 1):
            article_data = self.parse_single_article(str(article_id))
            
            if article_data:
                parsed_articles.append(article_data)
            
            # 요청 간 지연
            if delay > 0:
                time.sleep(delay)
        
        print(f"상세 파싱 완료: 총 {len(parsed_articles)}개 게시글")
        return parsed_articles
    
    def get_commentaries_from_db(self, book_name=None, chapter=None, verse=None, commentary_name=None, limit=None):
        """
        데이터베이스에서 주석 조회
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM commentaries WHERE 1=1"
        params = []
        
        if book_name:
            query += " AND book_name = ?"
            params.append(book_name)
        
        if chapter:
            query += " AND chapter = ?"
            params.append(chapter)
        
        if verse:
            query += " AND verse = ?"
            params.append(verse)
        
        if commentary_name:
            query += " AND commentary_name LIKE ?"
            params.append(f"%{commentary_name}%")
        
        query += " ORDER BY book_code, chapter, verse"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        commentaries = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return commentaries
    
    def get_statistics(self):
        """
        주석 데이터베이스 통계 정보
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 전체 주석 수
        cursor.execute("SELECT COUNT(*) FROM commentaries")
        total_count = cursor.fetchone()[0]
        
        # 성경책별 주석 수
        cursor.execute("""
            SELECT book_name, COUNT(*) as count 
            FROM commentaries 
            GROUP BY book_name 
            ORDER BY book_code
        """)
        book_stats = cursor.fetchall()
        
        # 주석별 통계
        cursor.execute("""
            SELECT commentary_name, COUNT(*) as count 
            FROM commentaries 
            GROUP BY commentary_name 
            ORDER BY count DESC
        """)
        commentary_stats = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_commentaries': total_count,
            'books': dict(book_stats),
            'commentary_types': dict(commentary_stats)
        }
    
    def export_to_json(self, filename, book_name=None, commentary_name=None):
        """
        주석 데이터를 JSON으로 내보내기
        """
        commentaries = self.get_commentaries_from_db(
            book_name=book_name, 
            commentary_name=commentary_name
        )
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(commentaries, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"JSON 내보내기 완료: {filename} ({len(commentaries)}개 주석)")


def main():
    """
    메인 함수 - 고급 파서 사용 예제
    """
    parser = AdvancedHochmaParser()
    
    print("고급 호크마 성경주석 파서")
    print("=" * 50)
    
    while True:
        print("\n선택할 작업:")
        print("1. 단일 게시글 상세 파싱")
        print("2. 범위 게시글 상세 파싱")
        print("3. 주석 데이터베이스 조회")
        print("4. JSON 내보내기")
        print("5. 통계 보기")
        print("6. 종료")
        
        choice = input("\n선택 (1-6): ").strip()
        
        if choice == '1':
            article_id = input("게시글 ID를 입력하세요: ").strip()
            if article_id:
                result = parser.parse_single_article(article_id)
                if result:
                    print(f"주석명: {result['commentary_name']}")
                    print(f"성경책: {result['book_name']} {result['chapter']}장")
                    print(f"절별 주석 수: {len(result['verse_commentaries'])}개")
        
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
            chapter = input("장 번호 (전체 조회시 엔터): ").strip()
            chapter = int(chapter) if chapter else None
            verse = input("절 번호 (전체 조회시 엔터): ").strip()
            verse = int(verse) if verse else None
            limit = input("조회 개수 제한 (전체 조회시 엔터): ").strip()
            limit = int(limit) if limit else None
            
            commentaries = parser.get_commentaries_from_db(
                book_name=book_name, 
                chapter=chapter, 
                verse=verse, 
                limit=limit
            )
            
            print(f"\n조회 결과: {len(commentaries)}개")
            for comm in commentaries[:5]:
                print(f"- {comm['commentary_name']} | {comm['book_name']} {comm['chapter']}:{comm['verse']} | {comm['text'][:50]}...")
            
            if len(commentaries) > 5:
                print(f"... 및 {len(commentaries) - 5}개 더")
        
        elif choice == '4':
            filename = input("저장할 파일명 (.json): ").strip()
            if not filename.endswith('.json'):
                filename += '.json'
            
            book_name = input("성경책 이름 (전체 내보내기시 엔터): ").strip() or None
            commentary_name = input("주석명 (전체 내보내기시 엔터): ").strip() or None
            parser.export_to_json(filename, book_name=book_name, commentary_name=commentary_name)
        
        elif choice == '5':
            stats = parser.get_statistics()
            print(f"\n=== 주석 통계 정보 ===")
            print(f"총 주석 수: {stats['total_commentaries']:,}개")
            
            print(f"\n주석 유형별:")
            for name, count in stats['commentary_types'].items():
                print(f"  {name}: {count:,}개")
            
            print(f"\n성경책별 주석 수:")
            for book, count in list(stats['books'].items())[:10]:
                print(f"  {book}: {count:,}개")
            
            if len(stats['books']) > 10:
                print(f"  ... 및 {len(stats['books']) - 10}개 성경책 더")
        
        elif choice == '6':
            print("프로그램을 종료합니다.")
            break
        
        else:
            print("올바른 선택지를 입력해주세요.")


if __name__ == "__main__":
    main() 