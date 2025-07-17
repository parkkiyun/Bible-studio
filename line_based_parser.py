import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import re
from urllib.parse import urljoin
import json
from datetime import datetime
import pandas as pd
import os

class LineBasedHochmaParser:
    def __init__(self, db_path="bible_database.db"):
        """
        줄바꿈 기반 호크마 성경주석 파서
        - 19:11 (단일 절)
        - 19:23,24 (콤마로 구분된 여러 절)  
        - 19:10-14 (하이픈으로 구분된 범위)
        """
        self.base_url = "https://nocr.net"
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session.headers.update(self.headers)
        self.db_path = db_path
    
    def get_book_code(self, book_name):
        """성경책 이름으로부터 book_code 조회"""
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
        return book_mapping.get(book_name, 999)
    
    def fetch_page(self, url, timeout=10):
        """웹 페이지 가져오기"""
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
    
    def is_verse_separator(self, line):
        """줄이 절 구분자인지 판단"""
        line = line.strip()
        if not line:
            return False, []
        
        # 절 구분자 패턴들
        patterns = [
            r'^(\d+):(\d+)$',                      # 19:11
            r'^(\d+):(\d+(?:,\d+)+)$',             # 19:23,24
            r'^(\d+):(\d+)-(\d+)$',                # 19:10-14
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                return True, self.parse_verse_numbers(match.groups())
        
        return False, []
    
    def parse_verse_numbers(self, groups):
        """매치된 그룹에서 절 번호들 추출"""
        verses = []
        
        if len(groups) == 2:  # 단일 절 또는 콤마 구분
            chapter = int(groups[0])
            verse_part = groups[1]
            
            if ',' in verse_part:
                # 콤마로 구분된 절들 (19:23,24)
                verse_numbers = verse_part.split(',')
                for v in verse_numbers:
                    verses.append((chapter, int(v.strip())))
            else:
                # 단일 절 (19:11)
                verses.append((chapter, int(verse_part)))
                
        elif len(groups) == 3:  # 범위 (19:10-14)
            chapter = int(groups[0])
            start_verse = int(groups[1])
            end_verse = int(groups[2])
            
            for v in range(start_verse, end_verse + 1):
                verses.append((chapter, v))
        
        return verses
    
    def extract_line_based_commentary(self, soup, url):
        """줄바꿈 기반 주석 데이터 추출"""
        article_data = {
            'url': url,
            'title': '',
            'commentary_name': '',
            'book_name': '',
            'chapter': '',
            'verse_commentaries': [],
            'pattern_info': {}
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
            title_match = re.search(r'([^,]+),\s*([가-힣]+)\s*(\d+)장', article_data['title'])
            if title_match:
                article_data['commentary_name'] = title_match.group(1).strip()
                article_data['book_name'] = title_match.group(2).strip()
                article_data['chapter'] = title_match.group(3).strip()
        
        # 3. 본문에서 줄바꿈 기반 절별 주석 추출
        content_element = soup.find(class_='xe_content') or soup.find(class_='rd_body') or soup.find(class_='rhymix_content')
        
        if content_element:
            content_text = content_element.get_text(strip=True)
            lines = content_text.split('\n')
            
            verse_separators = []
            for i, line in enumerate(lines):
                is_separator, verses = self.is_verse_separator(line)
                if is_separator:
                    verse_separators.append((i, line.strip(), verses))
            
            print(f"📋 발견된 절 구분자: {len(verse_separators)}개")
            
            if verse_separators:
                article_data['pattern_info'] = {
                    'type': 'line_based_verses',
                    'count': len(verse_separators)
                }
                
                # 각 절 구분자에 대해 내용 추출
                for j, (line_idx, separator_text, verses) in enumerate(verse_separators):
                    # 다음 절 구분자까지의 내용 추출
                    if j + 1 < len(verse_separators):
                        next_line_idx = verse_separators[j + 1][0]
                    else:
                        next_line_idx = len(lines)
                    
                    # 절 구분자 다음 줄부터 내용 추출
                    content_lines = lines[line_idx + 1:next_line_idx]
                    verse_content = '\n'.join(content_lines).strip()
                    
                    # 빈 줄 정리
                    verse_content = re.sub(r'\n\s*\n', '\n\n', verse_content)
                    
                    if verse_content and len(verse_content) > 10:
                        # 모든 관련 절에 같은 내용 추가
                        for chapter, verse in verses:
                            article_data['verse_commentaries'].append({
                                'chapter': chapter,
                                'verse': verse,
                                'commentary': verse_content,
                                'separator': separator_text
                            })
            
            # 절 구분자가 없는 경우 전체 텍스트를 하나의 주석으로 처리
            elif len(content_text) > 100:
                if article_data['chapter']:
                    article_data['verse_commentaries'].append({
                        'chapter': int(article_data['chapter']),
                        'verse': 1,
                        'commentary': content_text,
                        'separator': 'whole_chapter'
                    })
                    article_data['pattern_info'] = {
                        'type': 'whole_chapter',
                        'count': 1
                    }
        
        return article_data
    
    def parse_to_excel(self, article_id, excel_filename=None):
        """단일 게시글을 파싱하여 엑셀 파일로 저장"""
        url = f"{self.base_url}/com_kor_hochma/{article_id}"
        
        print(f"파싱 중: {url}")
        
        response = self.fetch_page(url)
        if not response:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        article_data = self.extract_line_based_commentary(soup, url)
        
        if not article_data['verse_commentaries']:
            print(f"✗ 주석 데이터 추출 실패: {url}")
            return None
        
        # Excel 파일명 생성
        if not excel_filename:
            pattern_info = article_data['pattern_info'].get('type', 'unknown')
            excel_filename = f"hochma_{article_data['book_name']}_{article_data['chapter']}장_{pattern_info}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # DataFrame 생성
        excel_data = []
        for verse_data in article_data['verse_commentaries']:
            excel_data.append({
                'ID': f"{article_data['book_name']}_{verse_data['chapter']}_{verse_data['verse']}",
                '주석명': article_data['commentary_name'],
                '성경책': article_data['book_name'],
                '성경책_코드': self.get_book_code(article_data['book_name']),
                '장': verse_data['chapter'],
                '절': verse_data['verse'],
                '주석_내용': verse_data['commentary'],
                '버전': f"{article_data['commentary_name']}-commentary",
                '원본_URL': article_data['url'],
                '파싱_날짜': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                '내용_길이': len(verse_data['commentary']),
                '패턴_유형': article_data['pattern_info'].get('type', 'unknown'),
                '절_구분자': verse_data.get('separator', '')
            })
        
        df = pd.DataFrame(excel_data)
        
        # Excel 파일로 저장
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='주석데이터', index=False)
            
            # 절 구분자별 통계
            separator_stats = df['절_구분자'].value_counts().to_dict()
            separator_data = {
                '절_구분자': list(separator_stats.keys()),
                '개수': list(separator_stats.values())
            }
            separator_df = pd.DataFrame(separator_data)
            separator_df.to_excel(writer, sheet_name='절구분자_통계', index=False)
            
            # 요약 시트 생성
            summary_data = {
                '항목': ['주석명', '성경책', '장', '총 절 수', '고유 절 수', '평균 내용 길이', '패턴 유형', '파싱 날짜', '원본 URL'],
                '값': [
                    article_data['commentary_name'],
                    article_data['book_name'],
                    article_data['chapter'],
                    len(article_data['verse_commentaries']),
                    df[['장', '절']].drop_duplicates().shape[0],
                    round(df['내용_길이'].mean()),
                    article_data['pattern_info'].get('type', 'unknown'),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    article_data['url']
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='요약정보', index=False)
        
        print(f"✓ Excel 저장 완료: {excel_filename}")
        print(f"  - {article_data['book_name']} {article_data['chapter']}장")
        print(f"  - {len(article_data['verse_commentaries'])}개 절 ({article_data['pattern_info'].get('type', 'unknown')} 패턴)")
        print(f"  - 고유 절 수: {df[['장', '절']].drop_duplicates().shape[0]}개")
        print(f"  - 평균 내용 길이: {round(df['내용_길이'].mean())}자")
        
        return {
            'excel_file': excel_filename,
            'article_data': article_data,
            'dataframe': df
        }
    
    def excel_to_database(self, excel_file):
        """엑셀 파일의 데이터를 데이터베이스에 저장"""
        if not os.path.exists(excel_file):
            print(f"엑셀 파일을 찾을 수 없습니다: {excel_file}")
            return False
        
        # 엑셀 파일 읽기
        df = pd.read_excel(excel_file, sheet_name='주석데이터')
        
        # 데이터베이스 연결 및 테이블 생성
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # commentaries 테이블 생성
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
                pattern_type TEXT,
                verse_separator TEXT,
                parsed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 데이터 삽입
        saved_count = 0
        for _, row in df.iterrows():
            cursor.execute('''
                INSERT OR REPLACE INTO commentaries 
                (book_name, book_code, chapter, verse, text, version, verse_title, 
                 commentary_name, original_url, pattern_type, verse_separator, parsed_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['성경책'],
                row['성경책_코드'],
                row['장'],
                row['절'],
                row['주석_내용'],
                row['버전'],
                None,
                row['주석명'],
                row['원본_URL'],
                row.get('패턴_유형', 'unknown'),
                row.get('절_구분자', ''),
                row['파싱_날짜']
            ))
            saved_count += 1
        
        conn.commit()
        conn.close()
        
        print(f"✓ 데이터베이스 저장 완료: {saved_count}개 절")
        return True


def main():
    """메인 함수"""
    parser = LineBasedHochmaParser()
    
    print("줄바꿈 기반 호크마 성경주석 파서")
    print("지원 패턴: 19:11, 19:23,24, 19:10-14")
    print("=" * 50)
    
    while True:
        print("\n선택할 작업:")
        print("1. 단일 게시글 파싱")
        print("2. 엑셀 파일 → 데이터베이스 저장")
        print("3. 종료")
        
        choice = input("\n선택 (1-3): ").strip()
        
        if choice == '1':
            article_id = input("게시글 ID를 입력하세요: ").strip()
            excel_filename = input("Excel 파일명 (엔터시 자동생성): ").strip() or None
            
            if article_id:
                result = parser.parse_to_excel(article_id, excel_filename)
                if result:
                    print(f"\n📁 파일 위치: {result['excel_file']}")
                    
                    save_to_db = input("\n데이터베이스에도 저장하시겠습니까? (y/n): ").strip().lower()
                    if save_to_db == 'y':
                        parser.excel_to_database(result['excel_file'])
        
        elif choice == '2':
            excel_file = input("엑셀 파일 경로를 입력하세요: ").strip()
            parser.excel_to_database(excel_file)
        
        elif choice == '3':
            print("프로그램을 종료합니다.")
            break
        
        else:
            print("올바른 선택지를 입력해주세요.")


if __name__ == "__main__":
    main() 