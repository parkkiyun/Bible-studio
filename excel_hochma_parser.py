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

class ExcelHochmaParser:
    def __init__(self, db_path="bible_database.db"):
        """
        엑셀 우선 저장 호크마 성경주석 파서
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
    
    def extract_detailed_commentary(self, soup, url):
        """상세한 주석 데이터 추출"""
        article_data = {
            'url': url,
            'title': '',
            'commentary_name': '',
            'book_name': '',
            'chapter': '',
            'verse_commentaries': []
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
        
        # 3. 본문에서 절별 주석 추출
        content_element = soup.find(class_='xe_content') or soup.find(class_='rd_body') or soup.find(class_='rhymix_content')
        
        if content_element:
            content_text = content_element.get_text(strip=True)
            
            # 3개 이상 등호로 절 구분자 찾기 (수정된 패턴)
            verse_pattern = r'={3,}(\d+):(\d+)'
            verse_matches = list(re.finditer(verse_pattern, content_text))
            
            if verse_matches:
                for i, match in enumerate(verse_matches):
                    chapter_num = match.group(1)
                    verse_num = match.group(2)
                    
                    start_pos = match.end()
                    if i + 1 < len(verse_matches):
                        end_pos = verse_matches[i + 1].start()
                    else:
                        end_pos = len(content_text)
                    
                    verse_commentary = content_text[start_pos:end_pos].strip()
                    verse_commentary = re.sub(r'^절[^가-힣]*', '', verse_commentary)
                    verse_commentary = verse_commentary.strip()
                    
                    if verse_commentary and len(verse_commentary) > 10:
                        article_data['verse_commentaries'].append({
                            'chapter': int(chapter_num),
                            'verse': int(verse_num),
                            'commentary': verse_commentary
                        })
            
            # 절 구분자가 없는 경우 전체 텍스트를 하나의 주석으로 처리
            if not article_data['verse_commentaries'] and len(content_text) > 100:
                if article_data['chapter']:
                    article_data['verse_commentaries'].append({
                        'chapter': int(article_data['chapter']),
                        'verse': 1,
                        'commentary': content_text
                    })
        
        return article_data
    
    def parse_to_excel(self, article_id, excel_filename=None):
        """단일 게시글을 파싱하여 엑셀 파일로 저장"""
        url = f"{self.base_url}/com_kor_hochma/{article_id}"
        
        print(f"파싱 중: {url}")
        
        response = self.fetch_page(url)
        if not response:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        article_data = self.extract_detailed_commentary(soup, url)
        
        if not article_data['verse_commentaries']:
            print(f"✗ 주석 데이터 추출 실패: {url}")
            return None
        
        # Excel 파일명 생성
        if not excel_filename:
            excel_filename = f"hochma_{article_data['book_name']}_{article_data['chapter']}장_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
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
                '내용_길이': len(verse_data['commentary'])
            })
        
        df = pd.DataFrame(excel_data)
        
        # Excel 파일로 저장
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='주석데이터', index=False)
            
            # 요약 시트 생성
            summary_data = {
                '항목': ['주석명', '성경책', '장', '총 절 수', '평균 내용 길이', '파싱 날짜', '원본 URL'],
                '값': [
                    article_data['commentary_name'],
                    article_data['book_name'],
                    article_data['chapter'],
                    len(article_data['verse_commentaries']),
                    round(df['내용_길이'].mean()),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    article_data['url']
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='요약정보', index=False)
        
        print(f"✓ Excel 저장 완료: {excel_filename}")
        print(f"  - {article_data['book_name']} {article_data['chapter']}장")
        print(f"  - {len(article_data['verse_commentaries'])}개 절")
        print(f"  - 평균 내용 길이: {round(df['내용_길이'].mean())}자")
        
        return {
            'excel_file': excel_filename,
            'article_data': article_data,
            'dataframe': df
        }
    
    def parse_range_to_excel(self, start_id, end_id, excel_filename=None, delay=1):
        """범위 내의 게시글들을 파싱하여 하나의 엑셀 파일로 저장"""
        print(f"범위 파싱 시작: {start_id} ~ {end_id}")
        
        all_excel_data = []
        parsed_count = 0
        
        for article_id in range(start_id, end_id + 1):
            url = f"{self.base_url}/com_kor_hochma/{article_id}"
            print(f"파싱 중: {url}")
            
            response = self.fetch_page(url)
            if not response:
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            article_data = self.extract_detailed_commentary(soup, url)
            
            if article_data['verse_commentaries']:
                for verse_data in article_data['verse_commentaries']:
                    all_excel_data.append({
                        'ID': f"{article_data['book_name']}_{verse_data['chapter']}_{verse_data['verse']}",
                        '주석명': article_data['commentary_name'],
                        '성경책': article_data['book_name'],
                        '성경책_코드': self.get_book_code(article_data['book_name']),
                        '장': verse_data['chapter'],
                        '절': verse_data['verse'],
                        '주석_내용': verse_data['commentary'],
                        '버전': f"{article_data['commentary_name']}-commentary",
                        '원본_URL': article_data['url'],
                        '게시글_ID': article_id,
                        '파싱_날짜': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        '내용_길이': len(verse_data['commentary'])
                    })
                parsed_count += 1
                print(f"  ✓ {article_data['book_name']} {article_data['chapter']}장 ({len(article_data['verse_commentaries'])}개 절)")
            else:
                print(f"  ✗ 파싱 실패: {article_id}")
            
            if delay > 0:
                time.sleep(delay)
        
        if not all_excel_data:
            print("파싱된 데이터가 없습니다.")
            return None
        
        # Excel 파일명 생성
        if not excel_filename:
            excel_filename = f"hochma_range_{start_id}_{end_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        df = pd.DataFrame(all_excel_data)
        
        # Excel 파일로 저장
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='주석데이터', index=False)
            
            # 성경책별 요약
            book_summary = df.groupby('성경책').agg({
                '장': ['min', 'max', 'nunique'],
                '절': 'count',
                '내용_길이': 'mean'
            }).round(1)
            book_summary.columns = ['최소장', '최대장', '장수', '총절수', '평균길이']
            book_summary.to_excel(writer, sheet_name='성경책별_요약')
            
            # 전체 요약
            total_summary = {
                '항목': ['총 게시글 수', '총 절 수', '성경책 수', '평균 내용 길이', '파싱 날짜'],
                '값': [
                    parsed_count,
                    len(df),
                    df['성경책'].nunique(),
                    round(df['내용_길이'].mean()),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ]
            }
            summary_df = pd.DataFrame(total_summary)
            summary_df.to_excel(writer, sheet_name='전체_요약', index=False)
        
        print(f"\n✓ Excel 저장 완료: {excel_filename}")
        print(f"  - 총 {parsed_count}개 게시글, {len(df)}개 절")
        print(f"  - 평균 내용 길이: {round(df['내용_길이'].mean())}자")
        
        return {
            'excel_file': excel_filename,
            'dataframe': df,
            'parsed_count': parsed_count
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
                parsed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 데이터 삽입
        saved_count = 0
        for _, row in df.iterrows():
            cursor.execute('''
                INSERT OR REPLACE INTO commentaries 
                (book_name, book_code, chapter, verse, text, version, verse_title, 
                 commentary_name, original_url, parsed_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                row['파싱_날짜']
            ))
            saved_count += 1
        
        conn.commit()
        conn.close()
        
        print(f"✓ 데이터베이스 저장 완료: {saved_count}개 절")
        return True


def main():
    """메인 함수"""
    parser = ExcelHochmaParser()
    
    print("엑셀 우선 호크마 성경주석 파서")
    print("=" * 50)
    
    while True:
        print("\n선택할 작업:")
        print("1. 단일 게시글 → 엑셀 저장")
        print("2. 범위 게시글 → 엑셀 저장")
        print("3. 엑셀 파일 → 데이터베이스 저장")
        print("4. 종료")
        
        choice = input("\n선택 (1-4): ").strip()
        
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
            try:
                start_id = int(input("시작 ID: "))
                end_id = int(input("종료 ID: "))
                delay = float(input("지연 시간(초, 기본 1초): ") or "1")
                excel_filename = input("Excel 파일명 (엔터시 자동생성): ").strip() or None
                
                result = parser.parse_range_to_excel(start_id, end_id, excel_filename, delay)
                if result:
                    print(f"\n📁 파일 위치: {result['excel_file']}")
                    
                    save_to_db = input("\n데이터베이스에도 저장하시겠습니까? (y/n): ").strip().lower()
                    if save_to_db == 'y':
                        parser.excel_to_database(result['excel_file'])
            except ValueError:
                print("올바른 숫자를 입력해주세요.")
        
        elif choice == '3':
            excel_file = input("엑셀 파일 경로를 입력하세요: ").strip()
            parser.excel_to_database(excel_file)
        
        elif choice == '4':
            print("프로그램을 종료합니다.")
            break
        
        else:
            print("올바른 선택지를 입력해주세요.")


if __name__ == "__main__":
    main() 