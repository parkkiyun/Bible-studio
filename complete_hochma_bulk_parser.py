import requests
from bs4 import BeautifulSoup
import re
import sqlite3
import pandas as pd
import json
import time
from datetime import datetime
import os

class CompleteHochmaBulkParser:
    def __init__(self, db_path='bible_database.db'):
        self.db_path = db_path
        self.base_url = "https://nocr.net/com_kor_hochma"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # 통계 변수
        self.total_processed = 0
        self.successful_parses = 0
        self.failed_parses = 0
        self.total_verses = 0
        
        self.setup_database()
    
    def setup_database(self):
        """데이터베이스 테이블 설정"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # commentaries 테이블 생성 (기존 bible_database.db와 호환)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS commentaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                commentary_name TEXT,
                book_name TEXT,
                book_code TEXT,
                chapter INTEGER,
                verse INTEGER,
                text TEXT,
                version TEXT DEFAULT 'hochma',
                verse_title TEXT,
                article_id INTEGER,  -- Ensure this column exists
                url TEXT,  -- Ensure this column exists
                parsed_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Check if article_id column exists, and add it if not
        cursor.execute("PRAGMA table_info(commentaries)")
        columns = [info[1] for info in cursor.fetchall()]
        if 'article_id' not in columns:
            cursor.execute("ALTER TABLE commentaries ADD COLUMN article_id INTEGER")
            print("Added 'article_id' column to commentaries table.")
        
        # Check if url column exists, and add it if not
        cursor.execute("PRAGMA table_info(commentaries)")
        columns = [info[1] for info in cursor.fetchall()]
        if 'url' not in columns:
            cursor.execute("ALTER TABLE commentaries ADD COLUMN url TEXT")
            print("Added 'url' column to commentaries table.")

        # 인덱스 생성
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_commentaries_book_chapter_verse 
            ON commentaries(book_name, chapter, verse)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_commentaries_article_id 
            ON commentaries(article_id)
        ''')
        
        conn.commit()
        conn.close()
        print("Database table setup complete.")
    
    def load_article_list(self, json_file):
        """추출된 게시글 목록 로드"""
        print(f"Loading article list: {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        articles = data['links']
        print(f"  Total articles: {len(articles)} ")
        
        return articles
    
    def parse_single_article(self, article_id):
        """단일 게시글 파싱"""
        url = f"{self.base_url}/{article_id}"
        
        try:
            response = self.session.get(url, timeout=15)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                return None, f"HTTP {response.status_code}"
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 제목 추출
            title = self.extract_title(soup)
            if not title:
                return None, "제목 추출 실패"
            
            # 제목에서 성경책명과 장 추출
            book_info = self.extract_book_info(title)
            if not book_info:
                return None, "성경책 정보 추출 실패"
            
            # 본문 추출
            content = self.extract_content(soup)
            if not content:
                return None, "본문 추출 실패"
            
            # 절별로 파싱
            verses = self.parse_verses(content, book_info['book_name'], book_info['chapter'])
            
            if not verses:
                return None, "절 파싱 실패"
            
            return {
                'title': title,
                'book_name': book_info['book_name'],
                'chapter': book_info['chapter'],
                'verses': verses,
                'url': url
            }, None
            
        except Exception as e:
            return None, str(e)
    
    def extract_title(self, soup):
        """제목 추출"""
        # H1 태그에서 제목 찾기
        h1_tags = soup.find_all('h1')
        for h1 in h1_tags:
            text = h1.get_text(strip=True)
            if '호크마 주석' in text:
                return text
        
        # title 태그에서 제목 찾기
        title_tag = soup.find('title')
        if title_tag:
            text = title_tag.get_text(strip=True)
            if '호크마 주석' in text:
                return text
        
        return None
    
    def extract_book_info(self, title):
        """제목에서 성경책명과 장 추출"""
        pattern = r'호크마 주석[,\s]*([가-힣]+(?:상|하)?(?:전서|후서)?(?:일서|이서|삼서)?(?:복음)?(?:기)?(?:애가)?)\s*(\d+)장'
        match = re.search(pattern, title)
        
        if match:
            return {
                'book_name': match.group(1),
                'chapter': int(match.group(2))
            }
        
        return None
    
    def extract_content(self, soup):
        """본문 추출"""
        # 다양한 본문 선택자 시도
        selectors = [
            '.rhymix_content',
            '.xe_content', 
            '.rd_body',
            '#article_content',
            '.document_content'
        ]
        
        for selector in selectors:
            content_div = soup.select_one(selector)
            if content_div:
                # <br> 태그를 줄바꿈으로 변환
                for br in content_div.find_all('br'):
                    br.replace_with('\n')
                
                text = content_div.get_text()
                if text.strip():
                    return text
        
        return None
    
    def parse_verses(self, content, book_name, chapter):
        """본문을 절별로 파싱 (순차적 절 번호 검증 추가)"""
        verses = []
        
        # 모든 가능한 절 패턴을 찾는 통합 정규식
        # 패턴 예시: =1:1, =1:1-5, 1:1, 1:3,5
        # \b (word boundary)를 추가하여 숫자만 있는 경우의 오탐을 줄임
        chapter_verse_pattern = re.compile(
            r'\b={0,}' + re.escape(str(chapter)) + r':(\d+(?:-\d+)?(?:,\d+)*)\b'
        )
        
        matches = list(chapter_verse_pattern.finditer(content))
        
        if not matches:
            return []

        processed_matches = []
        expected_verse_num = 1 # 절은 무조건 순서대로 등장 (1, 2, 3...)

        for i, match in enumerate(matches):
            matched_verse_str_raw = match.group(1) # e.g., "1", "1-5", "3,5"
            
            # parse_verse_range를 사용하여 실제 절 번호 목록을 얻음
            current_match_verse_nums = self.parse_verse_range(matched_verse_str_raw)
            
            if not current_match_verse_nums:
                continue # 유효한 절 번호가 없으면 건너뜀

            first_verse_in_match = current_match_verse_nums[0]

            # 순차적 절 번호 검증
            if first_verse_in_match == expected_verse_num:
                # 이 매치는 유효한 주석 절 시작으로 간주
                processed_matches.append(match)
                # 다음 예상 절 번호 업데이트
                expected_verse_num = current_match_verse_nums[-1] + 1
            elif first_verse_in_match > expected_verse_num:
                # 예상 절 번호보다 크면, 중간에 누락된 절이 있거나 참조 구절일 수 있음
                # 여기서는 순차적 파싱을 위해 이 매치를 무시하고 다음 매치를 기다림
                # (만약 누락된 절을 포함해야 한다면 로직 변경 필요)
                # 현재는 참조 구절을 걸러내는 데 중점을 둠
                continue
            else: # first_verse_in_match < expected_verse_num
                # 이미 처리했거나 이전 절 번호이면 무시 (참조 구절)
                continue

        # 이제 유효한 매치들로만 절 내용을 추출
        verses = []
        for i, match in enumerate(processed_matches):
            matched_verse_str = match.group(1) # This is the verse string from the regex
            
            start_pos = match.end()
            end_pos = processed_matches[i+1].start() if i + 1 < len(processed_matches) else len(content)
            verse_content = content[start_pos:end_pos].strip()

            if verse_content:
                verse_nums = self.parse_verse_range(matched_verse_str)
                for verse_num in verse_nums:
                    verses.append({
                        'verse': verse_num,
                        'content': verse_content
                    })
        
        return verses
    
    def parse_verse_range(self, verse_str):
        """절 범위 파싱 (예: "37,38" 또는 "33-35")"""
        verse_nums = []
        
        if ',' in verse_str:
            # 콤마로 구분된 절들
            for v in verse_str.split(','):
                try:
                    verse_nums.append(int(v.strip()))
                except ValueError:
                    continue
        elif '-' in verse_str:
            # 하이픈으로 구분된 범위
            parts = verse_str.split('-')
            if len(parts) == 2:
                try:
                    start = int(parts[0].strip())
                    end = int(parts[1].strip())
                    verse_nums.extend(range(start, end + 1))
                except ValueError:
                    pass
        else:
            # 단일 절
            try:
                verse_nums.append(int(verse_str.strip()))
            except ValueError:
                pass
        
        return verse_nums
    
    def save_to_database(self, parsed_data, article_id):
        """파싱된 데이터를 데이터베이스에 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            for verse_data in parsed_data['verses']:
                cursor.execute('''
                    INSERT INTO commentaries 
                    (commentary_name, book_name, book_code, chapter, verse, text, article_id, url, parsed_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    '호크마 주석',
                    parsed_data['book_name'],
                    '', # Add an empty string for book_code
                    parsed_data['chapter'],
                    verse_data['verse'],
                    verse_data['content'],
                    article_id,
                    parsed_data['url'],
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
            
            conn.commit()
            return len(parsed_data['verses'])
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def save_to_excel(self, articles, output_file):
        """결과를 엑셀로 저장"""
        print(f"Excel file creation in progress: {output_file}")
        
        all_data = []
        summary_data = []
        
        for article in articles:
            if article['status'] == 'success' and article['parsed_data']:
                parsed = article['parsed_data']
                for verse in parsed['verses']:
                    all_data.append({
                        'article_id': article['article_id'],
                        'title': article['title'],
                        'book_name': parsed['book_name'],
                        'chapter': parsed['chapter'],
                        'verse': verse['verse'],
                        'content': verse['content'],
                        'content_length': len(verse['content']),
                        'url': parsed['url']
                    })
                
                summary_data.append({
                    'article_id': article['article_id'],
                    'title': article['title'],
                    'book_name': parsed['book_name'],
                    'chapter': parsed['chapter'],
                    'total_verses': len(parsed['verses']),
                    'avg_content_length': sum(len(v['content']) for v in parsed['verses']) / len(parsed['verses']),
                    'status': 'success'
                })
            else:
                summary_data.append({
                    'article_id': article['article_id'],
                    'title': article['title'],
                    'book_name': '',
                    'chapter': 0,
                    'total_verses': 0,
                    'avg_content_length': 0,
                    'status': article['error']
                })
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # 전체 주석 데이터
            df_all = pd.DataFrame(all_data)
            df_all.to_excel(writer, sheet_name='전체주석데이터', index=False)
            
            # 요약 정보
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='파싱요약', index=False)
            
            # 통계
            stats_data = {
                '항목': ['총 게시글 수', '성공적 파싱', '실패한 파싱', '총 절 수', '평균 절/게시글'],
                '값': [
                    self.total_processed,
                    self.successful_parses,
                    self.failed_parses,
                    self.total_verses,
                    self.total_verses / max(self.successful_parses, 1)
                ]
            }
            df_stats = pd.DataFrame(stats_data)
            df_stats.to_excel(writer, sheet_name='통계', index=False)
        
        print(f"Excel file saved: {output_file}")
    
    def bulk_parse(self, json_file, save_to_db=True, save_to_excel=True, batch_size=50):
        """대량 파싱 실행"""
        print("Hochma Commentary Bulk Parsing Start")
        print("=" * 60)
        
        # 게시글 목록 로드
        articles = self.load_article_list(json_file)
        self.total_processed = len(articles)
        
        print(f"Parsing target: {self.total_processed} articles")
        print(f"Database save: {'O' if save_to_db else 'X'}")
        print(f"Excel save: {'O' if save_to_excel else 'X'}")
        print("=" * 60)
        
        start_time = time.time()
        results = []
        
        for i, article in enumerate(articles, 1):
            article_id = article['article_id']
            title = article['title']
            
            print(f"Progress: {i}/{self.total_processed} - Article {article_id}: ", end='')
            
            # 파싱 실행
            parsed_data, error = self.parse_single_article(article_id)
            
            if parsed_data:
                verse_count = len(parsed_data['verses'])
                print(f"{verse_count} verses")
                
                # 데이터베이스 저장
                if save_to_db:
                    try:
                        saved_count = self.save_to_database(parsed_data, article_id)
                        self.total_verses += saved_count
                    except Exception as e:
                        print(f"  DB save failed: {e}")
                
                results.append({
                    'article_id': article['article_id'],
                    'title': title,
                    'status': 'success',
                    'parsed_data': parsed_data,
                    'verse_count': verse_count,
                    'error': None
                })
                
                self.successful_parses += 1
            else:
                print(f"Parsing failed")
                results.append({
                    'article_id': article['article_id'],
                    'title': title,
                    'status': 'failed',
                    'parsed_data': None,
                    'verse_count': 0,
                    'error': error
                })
                
                self.failed_parses += 1
            
            # 진행률 표시
            if i % 50 == 0:
                elapsed = time.time() - start_time
                progress = (i / self.total_processed) * 100
                print(f"Progress: {progress:.1f}% ({i}/{self.total_processed}) - Elapsed: {elapsed:.1f}s")
            
            # 요청 간격 (서버 부하 방지)
            time.sleep(0.1)
        
        # 최종 결과
        elapsed_time = time.time() - start_time
        print(f"\nParsing complete!")
        print(f"  Total processing time: {elapsed_time:.1f}s")
        print(f"  Success: {self.successful_parses}")
        print(f"  Failed: {self.failed_parses}")
        print(f"  Total verses: {self.total_verses}")
        print(f"  Success rate: {(self.successful_parses/self.total_processed)*100:.1f}%")
        
        # 엑셀 저장
        if save_to_excel:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            excel_file = f"complete_hochma_parsed_{timestamp}.xlsx"
            self.save_to_excel(results, excel_file)
        
        return results

def main():
    """메인 함수"""
    print("Hochma Commentary Complete Parsing System")
    print("=" * 50)
    
    # JSON 파일 확인
    json_files = [f for f in os.listdir('.') if f.startswith('hochma_all_links_') and f.endswith('.json')]
    
    if not json_files:
        print("No article list JSON file found.")
        print("   Please run extract_all_hochma_links.py first.")
        return
    
    # 가장 최근 파일 사용
    json_file = sorted(json_files)[-1]
    print(f"Using article list: {json_file}")
    
    # 파서 초기화
    parser = CompleteHochmaBulkParser()
    
    # 대량 파싱 실행
    results = parser.bulk_parse(
        json_file=json_file,
        save_to_db=False,
        save_to_excel=True
    )
    
    print(f"\nAll tasks complete!")

if __name__ == "__main__":
    main()