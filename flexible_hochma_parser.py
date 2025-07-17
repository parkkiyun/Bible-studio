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

class FlexibleHochmaParser:
    def __init__(self, db_path="bible_database.db"):
        """
        유연한 호크마 성경주석 파서 - 다양한 절 구분 패턴 지원
        """
        self.base_url = "https://nocr.net"
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session.headers.update(self.headers)
        self.db_path = db_path
        self.bible_verse_counts = self._load_bible_verse_counts()

    def _load_bible_verse_counts(self):
        try:
            with open('bible_verse_counts.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("bible_verse_counts.json 파일을 찾을 수 없습니다. 절 수 검증이 비활성화됩니다.")
            return {}
    
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
    
    def detect_verse_pattern(self, content_text):
        """텍스트에서 절 구분 패턴 감지"""
        patterns = {
            'equals_4': r'====(\d+):(\d+)절?',
            'equals_3': r'===(\d+):(\d+)절?',
            'equals_any': r'={3,}(\d+):(\d+)절?',
            'line_start': r'^(\d+):(\d+)절?$',
        }
        
        pattern_counts = {}
        for pattern_name, pattern in patterns.items():
            if pattern_name == 'line_start':
                lines = content_text.split('\n')
                matches = []
                for i, line in enumerate(lines):
                    line = line.strip()
                    match = re.match(pattern, line)
                    if match:
                        matches.append((i, match.group(1), match.group(2)))
                pattern_counts[pattern_name] = matches
            else:
                matches = list(re.finditer(pattern, content_text))
                pattern_counts[pattern_name] = [(m.start(), m.group(1), m.group(2)) for m in matches]
        
        best_pattern = None
        max_count = 0
        
        for pattern_name, matches in pattern_counts.items():
            if len(matches) > max_count:
                max_count = len(matches)
                best_pattern = pattern_name
        
        return best_pattern, pattern_counts[best_pattern] if best_pattern else []
    
    def parse_verses_by_pattern(self, content_text, pattern_type, matches, book_name, chapter_num):
        """패턴에 따라 절별로 분할하고, 예상 절 수에 맞춰 정규화"""
        parsed_verses = {}
        
        if pattern_type == 'line_start':
            lines = content_text.split('\n')
            for i, (line_idx, chapter, verse) in enumerate(matches):
                current_verse = int(verse)
                current_chapter = int(chapter)
                
                # 다음 절의 시작 위치 찾기
                next_line_idx = len(lines)
                if i + 1 < len(matches):
                    next_line_idx = matches[i + 1][0]
                
                verse_content_lines = lines[line_idx + 1:next_line_idx]
                verse_content = '\n'.join(verse_content_lines).strip()
                verse_content = re.sub(r'\n\s*\n', '\n\n', verse_content)
                
                if verse_content.strip():
                    parsed_verses[(current_chapter, current_verse)] = verse_content
        else:
            for i, (pos, chapter, verse) in enumerate(matches):
                current_verse = int(verse)
                current_chapter = int(chapter)
                
                start_pos = content_text.find('\n', pos)
                if start_pos == -1:
                    continue
                start_pos += 1
                
                if i + 1 < len(matches):
                    end_pos = matches[i + 1][0]
                else:
                    end_pos = len(content_text)
                
                verse_content = content_text[start_pos:end_pos].strip()
                verse_content = re.sub(r'\n\s*\n', '\n\n', verse_content)
                
                if verse_content.strip():
                    parsed_verses[(current_chapter, current_verse)] = verse_content

        # 예상 절 수에 맞춰 정규화
        normalized_verse_commentaries = []
        if book_name in self.bible_verse_counts and chapter_num <= len(self.bible_verse_counts[book_name]):
            expected_verses_in_chapter = self.bible_verse_counts[book_name][chapter_num - 1]
            for i in range(1, expected_verses_in_chapter + 1):
                commentary_content = parsed_verses.get((chapter_num, i), '[누락된 절]')
                normalized_verse_commentaries.append({
                    'chapter': chapter_num,
                    'verse': i,
                    'commentary': commentary_content
                })
        else:
            # 예상 절 수 정보가 없으면 파싱된 절만 사용
            for (chap, ver), content in parsed_verses.items():
                normalized_verse_commentaries.append({
                    'chapter': chap,
                    'verse': ver,
                    'commentary': content
                })
            # 파싱된 절이 없는데 전체 장으로 처리된 경우
            if not normalized_verse_commentaries and len(content_text) > 100:
                normalized_verse_commentaries.append({
                    'chapter': chapter_num,
                    'verse': 1,
                    'commentary': content_text
                })

        return normalized_verse_commentaries
    
    def extract_flexible_commentary(self, soup, url):
        """유연한 주석 데이터 추출"""
        article_data = {
            'url': url,
            'title': '',
            'commentary_name': '',
            'book_name': '',
            'chapter': '',
            'verse_commentaries': [],
            'pattern_info': {}
        }
        
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
        
        if article_data['title']:
            title_match = re.search(r'([^,]+),\s*([가-힣]+)\s*(\d+)장', article_data['title'])
            if title_match:
                article_data['commentary_name'] = title_match.group(1).strip()
                article_data['book_name'] = title_match.group(2).strip()
                article_data['chapter'] = title_match.group(3).strip()
        
        content_element = soup.find(class_='xe_content') or soup.find(class_='rd_body') or soup.find(class_='rhymix_content')
        
        if content_element:
            content_text = content_element.get_text('\n', strip=True)
            pattern_type, matches = self.detect_verse_pattern(content_text)
            
            if pattern_type and matches:
                print(f"감지된 패턴: {pattern_type} ({len(matches)}개 절)")
                article_data['pattern_info'] = {
                    'type': pattern_type,
                    'count': len(matches)
                }
                verses = self.parse_verses_by_pattern(content_text, pattern_type, matches, article_data['book_name'], int(article_data['chapter']))
                article_data['verse_commentaries'] = verses
            
            elif len(content_text) > 100:
                if article_data['chapter']:
                    article_data['verse_commentaries'].append({
                        'chapter': int(article_data['chapter']),
                        'verse': 1,
                        'commentary': content_text
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
        article_data = self.extract_flexible_commentary(soup, url)
        
        if not article_data['verse_commentaries']:
            print(f"주석 데이터 추출 실패: {url}")
            return {
                'excel_file': None,
                'article_data': article_data,
                'dataframe': pd.DataFrame()
            }
        
        # 정규화된 절 목록 생성
        normalized_verse_commentaries = []
        book_name = article_data.get('book_name')
        chapter = article_data.get('chapter')

        if book_name and chapter and self.bible_verse_counts:
            chapter_int = int(chapter)
            if book_name in self.bible_verse_counts and chapter_int <= len(self.bible_verse_counts[book_name]):
                expected_verses_in_chapter = self.bible_verse_counts[book_name][chapter_int - 1]
                
                parsed_verses_map = {v['verse']: v for v in article_data['verse_commentaries']}
                
                for i in range(1, expected_verses_in_chapter + 1):
                    if i in parsed_verses_map:
                        normalized_verse_commentaries.append(parsed_verses_map[i])
                    else:
                        # 누락된 절에 대한 플레이스홀더 추가
                        normalized_verse_commentaries.append({
                            'chapter': chapter_int,
                            'verse': i,
                            'commentary': '[누락된 절]'
                        })
            else:
                # 성경책 또는 장 정보가 bible_verse_counts에 없는 경우 기존 데이터 사용
                normalized_verse_commentaries = article_data['verse_commentaries']
        else:
            # bible_verse_counts가 로드되지 않았거나 정보가 없는 경우 기존 데이터 사용
            normalized_verse_commentaries = article_data['verse_commentaries']

        article_data['verse_commentaries'] = normalized_verse_commentaries

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
                '패턴_유형': article_data['pattern_info'].get('type', 'unknown')
            })
        
        df = pd.DataFrame(excel_data)
        
        # Excel 파일로 저장
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='주석데이터', index=False)
            
            # 요약 시트 생성
            summary_data = {
                '항목': ['주석명', '성경책', '장', '총 절 수', '평균 내용 길이', '패턴 유형', '파싱 날짜', '원본 URL'],
                '값': [
                    article_data['commentary_name'],
                    article_data['book_name'],
                    article_data['chapter'],
                    len(article_data['verse_commentaries']),
                    round(df['내용_길이'].mean()) if not df.empty else 0,
                    article_data['pattern_info'].get('type', 'unknown'),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    article_data['url']
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='요약정보', index=False)
        
        print(f"Excel 저장 완료: {excel_filename}")
        print(f"  - {article_data['book_name']} {article_data['chapter']}장")
        print(f"  - {len(article_data['verse_commentaries'])}개 절 ({article_data['pattern_info'].get('type', 'unknown')} 패턴)")
        print(f"  - 평균 내용 길이: {round(df['내용_길이'].mean()) if not df.empty else 0}자")
        
        return {
            'excel_file': excel_filename,
            'article_data': article_data,
            'dataframe': df
        }

def main():
    """메인 함수"""
    parser = FlexibleHochmaParser()
    
    print("유연한 호크마 성경주석 파서 (다양한 패턴 지원)")
    print("=" * 60)
    
    while True:
        print("\n선택할 작업:")
        print("1. 단일 게시글 파싱 (자동 패턴 감지)")
        print("2. 엑셀 파일 → 데이터베이스 저장")
        print("3. 종료")
        
        choice = input("\n선택 (1-3): ").strip()
        
        if choice == '1':
            article_id = input("게시글 ID를 입력하세요: ").strip()
            excel_filename = input("Excel 파일명 (엔터시 자동생성): ").strip() or None
            
            if article_id:
                result = parser.parse_to_excel(article_id, excel_filename)
                if result and result['excel_file']:
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