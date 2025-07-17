import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import json
import time
from datetime import datetime
import os

class ExcelOnlyHochmaParser:
    def __init__(self):
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
    
    def load_article_list(self, json_file):
        """추출된 게시글 목록 로드"""
        print(f"📁 게시글 목록 로드 중: {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        articles = data['links']
        print(f"  총 게시글 수: {len(articles)}개")
        
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
        """본문을 절별로 파싱"""
        verses = []
        
        # 패턴 1: ====31:1 (4개 등호) 또는 ===31:1 (3개 등호)
        equals_pattern = r'={3,}(\d+):(\d+)'
        equals_matches = list(re.finditer(equals_pattern, content))
        
        if equals_matches:
            # 등호 패턴으로 절 구분
            for i, match in enumerate(equals_matches):
                verse_num = int(match.group(2))
                start_pos = match.end()
                
                if i < len(equals_matches) - 1:
                    end_pos = equals_matches[i + 1].start()
                    verse_content = content[start_pos:end_pos].strip()
                else:
                    verse_content = content[start_pos:].strip()
                
                if verse_content:
                    verses.append({
                        'verse': verse_num,
                        'content': verse_content
                    })
        else:
            # 패턴 2: 줄바꿈 기반 절 구분
            lines = content.split('\n')
            current_verse = None
            current_content = []
            
            verse_pattern = r'^(\d+):(\d+(?:,\d+)*(?:-\d+)*)$'
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                match = re.match(verse_pattern, line)
                if match:
                    # 이전 절 저장
                    if current_verse and current_content:
                        content_text = '\n'.join(current_content).strip()
                        if content_text:
                            # 콤마나 하이픈으로 구분된 절 처리
                            verse_nums = self.parse_verse_range(current_verse)
                            for verse_num in verse_nums:
                                verses.append({
                                    'verse': verse_num,
                                    'content': content_text
                                })
                    
                    # 새 절 시작
                    current_verse = match.group(2)
                    current_content = []
                else:
                    if current_verse:
                        current_content.append(line)
            
            # 마지막 절 저장
            if current_verse and current_content:
                content_text = '\n'.join(current_content).strip()
                if content_text:
                    verse_nums = self.parse_verse_range(current_verse)
                    for verse_num in verse_nums:
                        verses.append({
                            'verse': verse_num,
                            'content': content_text
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
    
    def save_to_excel(self, articles, output_file):
        """결과를 엑셀로 저장"""
        print(f"📊 엑셀 파일 생성 중: {output_file}")
        
        all_data = []
        summary_data = []
        book_stats = {}
        
        for article in articles:
            if article['status'] == 'success' and article['parsed_data']:
                parsed = article['parsed_data']
                book_name = parsed['book_name']
                chapter = parsed['chapter']
                
                # 성경책별 통계 업데이트
                if book_name not in book_stats:
                    book_stats[book_name] = {
                        'chapters': set(),
                        'total_verses': 0,
                        'total_content_length': 0
                    }
                
                book_stats[book_name]['chapters'].add(chapter)
                
                for verse in parsed['verses']:
                    all_data.append({
                        'article_id': article['article_id'],
                        'title': article['title'],
                        'book_name': book_name,
                        'chapter': chapter,
                        'verse': verse['verse'],
                        'content': verse['content'],
                        'content_length': len(verse['content']),
                        'url': parsed['url']
                    })
                    
                    book_stats[book_name]['total_verses'] += 1
                    book_stats[book_name]['total_content_length'] += len(verse['content'])
                
                summary_data.append({
                    'article_id': article['article_id'],
                    'title': article['title'],
                    'book_name': book_name,
                    'chapter': chapter,
                    'total_verses': len(parsed['verses']),
                    'avg_content_length': sum(len(v['content']) for v in parsed['verses']) / len(parsed['verses']),
                    'total_content_length': sum(len(v['content']) for v in parsed['verses']),
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
                    'total_content_length': 0,
                    'status': article['error']
                })
        
        # 성경책별 통계 정리
        book_summary = []
        for book_name, stats in book_stats.items():
            book_summary.append({
                'book_name': book_name,
                'chapters_count': len(stats['chapters']),
                'chapters_list': ', '.join(map(str, sorted(stats['chapters']))),
                'total_verses': stats['total_verses'],
                'avg_verse_length': stats['total_content_length'] / max(stats['total_verses'], 1),
                'total_content_length': stats['total_content_length']
            })
        
        # 엑셀 파일 생성
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # 1. 전체 주석 데이터
            if all_data:
                df_all = pd.DataFrame(all_data)
                df_all.to_excel(writer, sheet_name='전체주석데이터', index=False)
            
            # 2. 파싱 요약
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='파싱요약', index=False)
            
            # 3. 성경책별 통계
            if book_summary:
                df_books = pd.DataFrame(book_summary)
                df_books = df_books.sort_values('book_name')
                df_books.to_excel(writer, sheet_name='성경책별통계', index=False)
            
            # 4. 전체 통계
            stats_data = {
                '항목': [
                    '총 게시글 수', 
                    '성공적 파싱', 
                    '실패한 파싱', 
                    '성공률(%)', 
                    '총 절 수', 
                    '평균 절/게시글',
                    '성경책 수',
                    '총 내용 길이'
                ],
                '값': [
                    self.total_processed,
                    self.successful_parses,
                    self.failed_parses,
                    round((self.successful_parses / max(self.total_processed, 1)) * 100, 1),
                    self.total_verses,
                    round(self.total_verses / max(self.successful_parses, 1), 1),
                    len(book_stats),
                    sum(len(item['content']) for item in all_data) if all_data else 0
                ]
            }
            df_stats = pd.DataFrame(stats_data)
            df_stats.to_excel(writer, sheet_name='전체통계', index=False)
        
        print(f"✅ 엑셀 파일 저장 완료: {output_file}")
        
        # 요약 정보 출력
        print(f"\n📊 파싱 결과 요약:")
        print(f"  📚 성경책: {len(book_stats)}권")
        print(f"  📄 총 절: {self.total_verses}개")
        print(f"  ✅ 성공: {self.successful_parses}개")
        print(f"  ❌ 실패: {self.failed_parses}개")
        
        return output_file
    
    def bulk_parse(self, json_file, max_articles=None):
        """대량 파싱 실행 (엑셀만 저장)"""
        print("📊 호크마 주석 엑셀 전용 파싱 시작")
        print("=" * 60)
        
        # 게시글 목록 로드
        articles = self.load_article_list(json_file)
        
        # 개수 제한 (테스트용)
        if max_articles:
            articles = articles[:max_articles]
            print(f"⚠️ 테스트 모드: 처음 {max_articles}개만 파싱")
        
        self.total_processed = len(articles)
        
        print(f"📊 파싱 대상: {self.total_processed}개 게시글")
        print("=" * 60)
        
        start_time = time.time()
        results = []
        
        for i, article in enumerate(articles, 1):
            article_id = article['article_id']
            title = article['title']
            
            print(f"진행: {i}/{self.total_processed} - 게시글 {article_id}: ", end='')
            
            # 파싱 실행
            parsed_data, error = self.parse_single_article(article_id)
            
            if parsed_data:
                verse_count = len(parsed_data['verses'])
                print(f"{verse_count}개 절")
                
                results.append({
                    'article_id': article_id,
                    'title': title,
                    'status': 'success',
                    'parsed_data': parsed_data,
                    'verse_count': verse_count,
                    'error': None
                })
                
                self.successful_parses += 1
                self.total_verses += verse_count
            else:
                print(f"파싱 실패 - {error}")
                results.append({
                    'article_id': article_id,
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
                print(f"진행률: {progress:.1f}% ({i}/{self.total_processed}) - 경과시간: {elapsed:.1f}초")
            
            # 요청 간격 (서버 부하 방지)
            time.sleep(0.1)
        
        # 최종 결과
        elapsed_time = time.time() - start_time
        print(f"\n🎉 파싱 완료!")
        print(f"  총 처리 시간: {elapsed_time:.1f}초")
        print(f"  성공: {self.successful_parses}개")
        print(f"  실패: {self.failed_parses}개")
        print(f"  총 절 수: {self.total_verses}개")
        print(f"  성공률: {(self.successful_parses/self.total_processed)*100:.1f}%")
        
        # 엑셀 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_file = f"complete_hochma_parsed_{timestamp}.xlsx"
        self.save_to_excel(results, excel_file)
        
        return results

def main():
    """메인 함수"""
    print("📖 호크마 주석 엑셀 전용 파싱 시스템")
    print("=" * 50)
    
    # JSON 파일 확인
    json_files = [f for f in os.listdir('.') if f.startswith('hochma_all_links_') and f.endswith('.json')]
    
    if not json_files:
        print("❌ 게시글 목록 JSON 파일을 찾을 수 없습니다.")
        print("   먼저 extract_all_hochma_links.py를 실행하세요.")
        return
    
    # 가장 최근 파일 사용
    json_file = sorted(json_files)[-1]
    print(f"📁 사용할 게시글 목록: {json_file}")
    
    # 파서 초기화
    parser = ExcelOnlyHochmaParser()
    
    # 사용자 선택
    print("\n🎯 파싱 모드를 선택하세요:")
    print("  1. 전체 파싱 (1,190개 모든 게시글)")
    print("  2. 테스트 파싱 (처음 50개만)")
    print("  3. 사용자 지정 개수")
    
    try:
        choice = input("선택 (1/2/3): ").strip()
        
        if choice == '1':
            max_articles = None
        elif choice == '2':
            max_articles = 50
        elif choice == '3':
            max_articles = int(input("파싱할 게시글 수: "))
        else:
            print("잘못된 선택입니다. 전체 파싱을 진행합니다.")
            max_articles = None
    except (ValueError, KeyboardInterrupt):
        print("전체 파싱을 진행합니다.")
        max_articles = None
    
    # 대량 파싱 실행
    results = parser.bulk_parse(
        json_file=json_file,
        max_articles=max_articles
    )
    
    print(f"\n✅ 모든 작업 완료!")

if __name__ == "__main__":
    main() 