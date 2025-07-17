import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from datetime import datetime
import json

class CorrectedHochmaParser:
    def __init__(self):
        self.base_url = "https://nocr.net/index.php?mid=com_kor_hochma&document_srl="
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # 성경책 정규화 매핑
        self.book_name_mapping = {
            '창세기': '창세기', '출애굽기': '출애굽기', '레위기': '레위기', '민수기': '민수기', '신명기': '신명기',
            '여호수아': '여호수아', '사사기': '사사기', '룻기': '룻기', 
            '사무엘상': '사무엘상', '사무엘하': '사무엘하', '열왕기상': '열왕기상', '열왕기하': '열왕기하',
            '역대상': '역대상', '역대하': '역대하', '에스라': '에스라', '느헤미야': '느헤미야', '에스더': '에스더',
            '욥기': '욥기', '시편': '시편', '잠언': '잠언', '전도서': '전도서', '아가': '아가',
            '이사야': '이사야', '예레미야': '예레미야', '예레미야애가': '예레미야애가', '에스겔': '에스겔', '다니엘': '다니엘',
            '호세아': '호세아', '요엘': '요엘', '아모스': '아모스', '오바댜': '오바댜', '요나': '요나', 
            '미가': '미가', '나훔': '나훔', '하박국': '하박국', '스바냐': '스바냐', '학개': '학개', '스가랴': '스가랴', '말라기': '말라기',
            '마태복음': '마태복음', '마가복음': '마가복음', '누가복음': '누가복음', '요한복음': '요한복음', '사도행전': '사도행전',
            '로마서': '로마서', '고린도전서': '고린도전서', '고린도후서': '고린도후서', '갈라디아서': '갈라디아서',
            '에베소서': '에베소서', '빌립보서': '빌립보서', '골로새서': '골로새서', 
            '데살로니가전서': '데살로니가전서', '데살로니가후서': '데살로니가후서',
            '디모데전서': '디모데전서', '디모데후서': '디모데후서', '디도서': '디도서', '빌레몬서': '빌레몬서',
            '히브리서': '히브리서', '야고보서': '야고보서', '베드로전서': '베드로전서', '베드로후서': '베드로후서',
            '요한일서': '요한일서', '요한이서': '요한이서', '요한삼서': '요한삼서', '유다서': '유다서', '요한계시록': '요한계시록'
        }

    def extract_title_and_info(self, article_id):
        """게시글에서 올바른 제목과 성경 정보 추출"""
        url = f"{self.base_url}{article_id}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                return None, None, None, None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # title 태그에서 제목 추출
            title_tag = soup.find('title')
            if not title_tag:
                return None, None, None, None
                
            title_text = title_tag.get_text(strip=True)
            
            # "호크마 주석, 창세기 01장 - 호크마 주석 - HANGL NOCR" 형식에서 정보 추출
            # 패턴: 호크마 주석, 성경책명 숫자장
            pattern = r'호크마 주석[,\s]*([가-힣]+(?:상|하)?(?:전서|후서)?(?:일서|이서|삼서)?(?:복음)?(?:기)?(?:애가)?)\s*(\d+)장'
            match = re.search(pattern, title_text)
            
            if not match:
                return title_text, None, None, None
            
            book_name_raw = match.group(1)
            chapter = int(match.group(2))
            
            # 성경책명 정규화
            book_name = self.book_name_mapping.get(book_name_raw, book_name_raw)
            
            return title_text, "호크마 주석", book_name, chapter
            
        except Exception as e:
            print(f"❌ 게시글 {article_id} 제목 추출 실패: {e}")
            return None, None, None, None

    def parse_article_content(self, article_id):
        """게시글 내용 파싱"""
        url = f"{self.base_url}{article_id}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 제목 정보 추출
            title, commentary_name, book_name, chapter = self.extract_title_and_info(article_id)
            
            if not book_name or not chapter:
                print(f"⚠️  게시글 {article_id}: 성경 정보 추출 실패")
                return []
            
            # 본문 내용 추출
            content_selectors = ['.xe_content', '.rd_body', '.rhymix_content']
            content_area = None
            
            for selector in content_selectors:
                content_area = soup.select_one(selector)
                if content_area:
                    break
            
            if not content_area:
                print(f"⚠️  게시글 {article_id}: 본문 영역을 찾을 수 없음")
                return []
            
            # <br> 태그를 \n으로 변환
            for br in content_area.find_all('br'):
                br.replace_with('\n')
            
            full_text = content_area.get_text()
            lines = [line.strip() for line in full_text.split('\n') if line.strip()]
            
            # 절별 파싱
            verses_data = []
            
            # 패턴 1: ====31:1 또는 ===31:1 형식
            equals_pattern = r'^={3,}(\d+):(\d+(?:,\d+)*(?:-\d+)*)$'
            
            # 패턴 2: 31:1 형식 (독립된 줄)  
            line_pattern = r'^(\d+):(\d+(?:,\d+)*(?:-\d+)*)$'
            
            current_verses = []
            current_content = []
            pattern_type = "none"
            
            for line in lines:
                # 패턴 1: equals 구분자
                equals_match = re.match(equals_pattern, line)
                if equals_match:
                    # 이전 절 저장
                    if current_verses and current_content:
                        content_text = '\n'.join(current_content).strip()
                        if content_text:
                            self._add_verses_data(verses_data, article_id, url, title, commentary_name, 
                                                book_name, chapter, current_verses, content_text, "equals")
                    
                    # 새 절 시작
                    ch = int(equals_match.group(1))
                    verses_str = equals_match.group(2)
                    current_verses = self._parse_verse_numbers(verses_str)
                    current_content = []
                    pattern_type = "equals"
                    continue
                
                # 패턴 2: 독립된 줄의 절 번호
                line_match = re.match(line_pattern, line)
                if line_match:
                    # 이전 절 저장
                    if current_verses and current_content:
                        content_text = '\n'.join(current_content).strip()
                        if content_text:
                            self._add_verses_data(verses_data, article_id, url, title, commentary_name, 
                                                book_name, chapter, current_verses, content_text, "lines")
                    
                    # 새 절 시작
                    ch = int(line_match.group(1))
                    verses_str = line_match.group(2)
                    current_verses = self._parse_verse_numbers(verses_str)
                    current_content = []
                    pattern_type = "lines"
                    continue
                
                # 내용 라인
                if current_verses:
                    current_content.append(line)
            
            # 마지막 절 저장
            if current_verses and current_content:
                content_text = '\n'.join(current_content).strip()
                if content_text:
                    self._add_verses_data(verses_data, article_id, url, title, commentary_name, 
                                        book_name, chapter, current_verses, content_text, pattern_type)
            
            # 절을 찾지 못한 경우 전체 내용을 1절로 저장
            if not verses_data and lines:
                full_content = '\n'.join(lines).strip()
                if full_content:
                    verses_data.append({
                        'article_id': article_id,
                        'url': url,
                        'title': title,
                        'commentary_name': commentary_name,
                        'book_name': book_name,
                        'chapter': chapter,
                        'verse': 1,
                        'content': full_content,
                        'content_length': len(full_content),
                        'pattern_type': 'none'
                    })
            
            return verses_data
            
        except Exception as e:
            print(f"❌ 게시글 {article_id} 파싱 실패: {e}")
            return []

    def _parse_verse_numbers(self, verses_str):
        """절 번호 문자열을 파싱하여 절 번호 리스트 반환"""
        verses = []
        
        for part in verses_str.split(','):
            part = part.strip()
            if '-' in part:
                # 범위: 33-35 -> [33, 34, 35]
                start, end = map(int, part.split('-'))
                verses.extend(range(start, end + 1))
            else:
                # 단일 절
                verses.append(int(part))
        
        return verses

    def _add_verses_data(self, verses_data, article_id, url, title, commentary_name, 
                        book_name, chapter, verses, content, pattern_type):
        """절 데이터를 추가"""
        for verse in verses:
            verses_data.append({
                'article_id': article_id,
                'url': url,
                'title': title,
                'commentary_name': commentary_name,
                'book_name': book_name,
                'chapter': chapter,
                'verse': verse,
                'content': content,
                'content_length': len(content),
                'pattern_type': pattern_type
            })

    def parse_multiple_articles(self, article_ids, progress_callback=None):
        """여러 게시글 파싱"""
        all_data = []
        failed_articles = []
        
        print(f"🚀 {len(article_ids)}개 게시글 파싱 시작...")
        start_time = time.time()
        
        for i, article_id in enumerate(article_ids):
            try:
                if progress_callback and i % 10 == 0:
                    progress_callback(i, len(article_ids))
                
                verses_data = self.parse_article_content(article_id)
                
                if verses_data:
                    all_data.extend(verses_data)
                    if i % 50 == 0:  # 50개마다 출력
                        print(f"  진행: {i+1}/{len(article_ids)} - 게시글 {article_id}: {len(verses_data)}개 절")
                else:
                    failed_articles.append(article_id)
                    print(f"  ❌ 게시글 {article_id}: 파싱 실패")
                
                # 요청 간격 조절
                time.sleep(0.1)
                
            except Exception as e:
                print(f"❌ 게시글 {article_id} 처리 중 오류: {e}")
                failed_articles.append(article_id)
        
        elapsed_time = time.time() - start_time
        print(f"\n✅ 파싱 완료!")
        print(f"  처리 시간: {elapsed_time:.1f}초")
        print(f"  성공: {len(article_ids) - len(failed_articles)}/{len(article_ids)}")
        print(f"  총 절 수: {len(all_data):,}")
        print(f"  실패한 게시글: {len(failed_articles)}개")
        
        return all_data, failed_articles

    def save_to_excel(self, data, filename=None):
        """엑셀로 저장"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"corrected_hochma_commentaries_{timestamp}.xlsx"
        
        if not data:
            print("❌ 저장할 데이터가 없습니다.")
            return
        
        print(f"💾 엑셀 파일로 저장 중: {filename}")
        
        df = pd.DataFrame(data)
        
        # 통계 생성
        stats_data = []
        
        # 성경책별 통계
        book_stats = df.groupby('book_name').agg({
            'article_id': 'nunique',
            'chapter': ['nunique', 'min', 'max'],
            'verse': 'count',
            'content_length': 'sum'
        }).round(2)
        
        for book in book_stats.index:
            if pd.notna(book):
                stats_data.append({
                    '성경책': book,
                    '게시글수': book_stats.loc[book, ('article_id', 'nunique')],
                    '장수': book_stats.loc[book, ('chapter', 'nunique')],
                    '최소장': book_stats.loc[book, ('chapter', 'min')],
                    '최대장': book_stats.loc[book, ('chapter', 'max')],
                    '절수': book_stats.loc[book, ('verse', 'count')],
                    '총글자수': book_stats.loc[book, ('content_length', 'sum')]
                })
        
        stats_df = pd.DataFrame(stats_data)
        
        # 요약 정보
        summary_data = [{
            '구분': '전체 통계',
            '값': f"게시글 {df['article_id'].nunique()}개, 성경책 {df['book_name'].nunique()}개, 절 {len(df):,}개"
        }, {
            '구분': '총 글자수',
            '값': f"{df['content_length'].sum():,}자"
        }, {
            '구분': '평균 절 길이',
            '값': f"{df['content_length'].mean():.0f}자"
        }]
        
        summary_df = pd.DataFrame(summary_data)
        
        # 엑셀 저장
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='호크마 주석 데이터', index=False)
            summary_df.to_excel(writer, sheet_name='요약 정보', index=False)
            stats_df.to_excel(writer, sheet_name='성경책별 통계', index=False)
        
        import os
        file_size = os.path.getsize(filename)
        file_size_mb = file_size / (1024 * 1024)
        print(f"✅ 저장 완료: {filename} ({file_size_mb:.1f}MB)")
        
        return filename

def load_article_ids():
    """이전에 발견한 게시글 ID 목록 로드"""
    try:
        with open('found_articles.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('article_ids', [])
    except:
        # 기본 범위로 시도
        return list(range(139393, 141927))

def main():
    """메인 함수"""
    print("🔧 호크마 주석 올바른 파싱 시작")
    print("=" * 50)
    
    # 게시글 ID 목록 로드
    article_ids = load_article_ids()
    print(f"📋 파싱할 게시글 수: {len(article_ids)}개")
    
    # 파서 생성
    parser = CorrectedHochmaParser()
    
    # 진행 상황 콜백
    def progress_callback(current, total):
        percent = (current / total) * 100
        print(f"  진행률: {percent:.1f}% ({current}/{total})")
    
    # 파싱 실행
    data, failed = parser.parse_multiple_articles(article_ids, progress_callback)
    
    if data:
        # 엑셀 저장
        filename = parser.save_to_excel(data)
        
        # 결과 분석
        df = pd.DataFrame(data)
        print(f"\n📊 파싱 결과 분석:")
        print(f"  총 절 수: {len(df):,}")
        print(f"  성경책 수: {df['book_name'].nunique()}")
        print(f"  게시글 수: {df['article_id'].nunique()}")
        
        # 성경책별 요약
        print(f"\n📚 성경책별 요약:")
        book_summary = df.groupby('book_name').agg({
            'chapter': 'nunique',
            'verse': 'count'
        }).sort_values('chapter', ascending=False)
        
        for book, stats in book_summary.head(10).iterrows():
            print(f"  {book}: {stats['chapter']}장, {stats['verse']}절")
    
    else:
        print("❌ 파싱된 데이터가 없습니다.")

if __name__ == "__main__":
    main() 