import requests
from bs4 import BeautifulSoup
import re
import sqlite3
import pandas as pd
import json
from collections import defaultdict
import time

class HochmaAvailabilityChecker:
    def __init__(self):
        self.base_url = "https://nocr.net/index.php?mid=com_kor_hochma&document_srl="
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Bible Database에서 성경 구조 가져오기
        self.bible_structure = self.load_bible_structure()

    def load_bible_structure(self):
        """Bible Database에서 성경책별 장 수 로드"""
        try:
            conn = sqlite3.connect('bible_database.db')
            
            query = """
            SELECT book_name, MAX(chapter) as max_chapter
            FROM verses 
            GROUP BY book_name 
            ORDER BY 
                CASE book_name
                    WHEN '창세기' THEN 1 WHEN '출애굽기' THEN 2 WHEN '레위기' THEN 3 WHEN '민수기' THEN 4 WHEN '신명기' THEN 5
                    WHEN '여호수아' THEN 6 WHEN '사사기' THEN 7 WHEN '룻기' THEN 8 WHEN '사무엘상' THEN 9 WHEN '사무엘하' THEN 10
                    WHEN '열왕기상' THEN 11 WHEN '열왕기하' THEN 12 WHEN '역대상' THEN 13 WHEN '역대하' THEN 14 WHEN '에스라' THEN 15
                    WHEN '느헤미야' THEN 16 WHEN '에스더' THEN 17 WHEN '욥기' THEN 18 WHEN '시편' THEN 19 WHEN '잠언' THEN 20
                    WHEN '전도서' THEN 21 WHEN '아가' THEN 22 WHEN '이사야' THEN 23 WHEN '예레미야' THEN 24 WHEN '예레미야애가' THEN 25
                    WHEN '에스겔' THEN 26 WHEN '다니엘' THEN 27 WHEN '호세아' THEN 28 WHEN '요엘' THEN 29 WHEN '아모스' THEN 30
                    WHEN '오바댜' THEN 31 WHEN '요나' THEN 32 WHEN '미가' THEN 33 WHEN '나훔' THEN 34 WHEN '하박국' THEN 35
                    WHEN '스바냐' THEN 36 WHEN '학개' THEN 37 WHEN '스가랴' THEN 38 WHEN '말라기' THEN 39 WHEN '마태복음' THEN 40
                    WHEN '마가복음' THEN 41 WHEN '누가복음' THEN 42 WHEN '요한복음' THEN 43 WHEN '사도행전' THEN 44 WHEN '로마서' THEN 45
                    WHEN '고린도전서' THEN 46 WHEN '고린도후서' THEN 47 WHEN '갈라디아서' THEN 48 WHEN '에베소서' THEN 49 WHEN '빌립보서' THEN 50
                    WHEN '골로새서' THEN 51 WHEN '데살로니가전서' THEN 52 WHEN '데살로니가후서' THEN 53 WHEN '디모데전서' THEN 54 WHEN '디모데후서' THEN 55
                    WHEN '디도서' THEN 56 WHEN '빌레몬서' THEN 57 WHEN '히브리서' THEN 58 WHEN '야고보서' THEN 59 WHEN '베드로전서' THEN 60
                    WHEN '베드로후서' THEN 61 WHEN '요한일서' THEN 62 WHEN '요한이서' THEN 63 WHEN '요한삼서' THEN 64 WHEN '유다서' THEN 65
                    WHEN '요한계시록' THEN 66 ELSE 999
                END
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            result = {}
            for _, row in df.iterrows():
                result[row['book_name']] = row['max_chapter']
            
            return result
            
        except Exception as e:
            print(f"❌ Bible Database 로드 실패: {e}")
            return {}

    def check_article_exists_and_get_title(self, article_id):
        """게시글이 존재하는지 확인하고 제목 추출"""
        url = f"{self.base_url}{article_id}"
        
        try:
            response = self.session.get(url, timeout=5)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                return False, None, None, None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # title 태그에서 제목 추출
            title_tag = soup.find('title')
            if not title_tag:
                return False, None, None, None
                
            title_text = title_tag.get_text(strip=True)
            
            # 호크마 주석 패턴 확인
            pattern = r'호크마 주석[,\s]*([가-힣]+(?:상|하)?(?:전서|후서)?(?:일서|이서|삼서)?(?:복음)?(?:기)?(?:애가)?)\s*(\d+)장'
            match = re.search(pattern, title_text)
            
            if match:
                book_name = match.group(1)
                chapter = int(match.group(2))
                return True, title_text, book_name, chapter
            else:
                return False, title_text, None, None
                
        except Exception as e:
            return False, None, None, None

    def scan_article_range(self, start_id, end_id, sample_interval=10):
        """게시글 ID 범위를 스캔하여 호크마 주석 찾기"""
        print(f"🔍 게시글 {start_id}~{end_id} 범위 스캔 (간격: {sample_interval})")
        
        found_articles = []
        book_chapters = defaultdict(set)
        
        sample_ids = list(range(start_id, end_id + 1, sample_interval))
        
        for i, article_id in enumerate(sample_ids):
            if i % 50 == 0:
                print(f"  진행: {i}/{len(sample_ids)} ({article_id})")
            
            exists, title, book_name, chapter = self.check_article_exists_and_get_title(article_id)
            
            if exists and book_name and chapter:
                found_articles.append({
                    'article_id': article_id,
                    'title': title,
                    'book_name': book_name,
                    'chapter': chapter
                })
                book_chapters[book_name].add(chapter)
                print(f"    ✅ {article_id}: {book_name} {chapter}장")
            
            time.sleep(0.05)  # 요청 간격
        
        return found_articles, dict(book_chapters)

    def detailed_scan_around_found_articles(self, found_articles, scan_range=5):
        """발견된 게시글 주변을 상세 스캔"""
        print(f"🔍 발견된 게시글 주변 상세 스캔 (범위: ±{scan_range})")
        
        additional_articles = []
        book_chapters = defaultdict(set)
        
        scanned_ids = set()
        
        for article in found_articles:
            base_id = article['article_id']
            
            # 주변 ID 스캔
            for offset in range(-scan_range, scan_range + 1):
                scan_id = base_id + offset
                
                if scan_id in scanned_ids:
                    continue
                scanned_ids.add(scan_id)
                
                exists, title, book_name, chapter = self.check_article_exists_and_get_title(scan_id)
                
                if exists and book_name and chapter:
                    # 이미 찾아진 것이 아닌 새로운 것만 추가
                    if not any(a['article_id'] == scan_id for a in found_articles):
                        additional_articles.append({
                            'article_id': scan_id,
                            'title': title,
                            'book_name': book_name,
                            'chapter': chapter
                        })
                        book_chapters[book_name].add(chapter)
                        print(f"    ✅ {scan_id}: {book_name} {chapter}장")
                
                time.sleep(0.02)
        
        return additional_articles, dict(book_chapters)

    def analyze_coverage(self, all_found_articles):
        """발견된 게시글들의 성경 커버리지 분석"""
        print(f"\n📊 호크마 주석 커버리지 분석")
        print("=" * 50)
        
        # 발견된 성경책-장 매핑
        found_coverage = defaultdict(set)
        for article in all_found_articles:
            found_coverage[article['book_name']].add(article['chapter'])
        
        coverage_report = []
        
        print(f"📚 성경책별 커버리지:")
        for book_name, max_chapter in self.bible_structure.items():
            found_chapters = found_coverage.get(book_name, set())
            coverage_percent = (len(found_chapters) / max_chapter) * 100 if max_chapter > 0 else 0
            
            missing_chapters = set(range(1, max_chapter + 1)) - found_chapters
            
            coverage_report.append({
                'book_name': book_name,
                'max_chapters': max_chapter,
                'found_chapters': len(found_chapters),
                'coverage_percent': coverage_percent,
                'missing_chapters': sorted(missing_chapters),
                'found_chapter_list': sorted(found_chapters)
            })
            
            status = "✅" if coverage_percent == 100 else "⚠️" if coverage_percent > 0 else "❌"
            print(f"  {status} {book_name}: {len(found_chapters)}/{max_chapter}장 ({coverage_percent:.1f}%)")
            
            if missing_chapters and len(missing_chapters) <= 10:
                print(f"    누락: {sorted(missing_chapters)}")
        
        # 전체 통계
        total_chapters = sum(self.bible_structure.values())
        total_found = sum(len(chapters) for chapters in found_coverage.values())
        overall_coverage = (total_found / total_chapters) * 100 if total_chapters > 0 else 0
        
        print(f"\n📈 전체 커버리지:")
        print(f"  총 성경 장 수: {total_chapters}")
        print(f"  발견된 장 수: {total_found}")
        print(f"  전체 커버리지: {overall_coverage:.1f}%")
        print(f"  발견된 성경책: {len(found_coverage)}/{len(self.bible_structure)}")
        
        return coverage_report

    def save_results(self, found_articles, coverage_report):
        """결과 저장"""
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        
        # 발견된 게시글 저장
        articles_df = pd.DataFrame(found_articles)
        articles_filename = f"hochma_available_articles_{timestamp}.xlsx"
        articles_df.to_excel(articles_filename, index=False)
        
        # 커버리지 리포트 저장
        coverage_df = pd.DataFrame(coverage_report)
        coverage_filename = f"hochma_coverage_report_{timestamp}.xlsx"
        coverage_df.to_excel(coverage_filename, index=False)
        
        # JSON으로도 저장
        json_data = {
            'scan_timestamp': timestamp,
            'found_articles': found_articles,
            'coverage_report': coverage_report
        }
        
        json_filename = f"hochma_availability_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 결과 저장:")
        print(f"  게시글 목록: {articles_filename}")
        print(f"  커버리지 리포트: {coverage_filename}")
        print(f"  JSON 데이터: {json_filename}")
        
        return articles_filename, coverage_filename, json_filename

def main():
    """메인 함수"""
    print("🔍 호크마 주석 사용 가능 성경책/장 분석")
    print("=" * 50)
    
    checker = HochmaAvailabilityChecker()
    
    if not checker.bible_structure:
        print("❌ Bible Database를 로드할 수 없습니다.")
        return
    
    print(f"📖 Bible Database 로드 완료: {len(checker.bible_structure)}개 성경책")
    
    # 1단계: 넓은 범위 샘플링 스캔
    print(f"\n1️⃣ 1단계: 넓은 범위 샘플링 스캔")
    found_articles_1, book_chapters_1 = checker.scan_article_range(139000, 142000, sample_interval=20)
    
    # 2단계: 발견된 게시글 주변 상세 스캔
    print(f"\n2️⃣ 2단계: 발견된 게시글 주변 상세 스캔")
    additional_articles, book_chapters_2 = checker.detailed_scan_around_found_articles(found_articles_1, scan_range=10)
    
    # 전체 결과 통합
    all_found_articles = found_articles_1 + additional_articles
    print(f"\n📊 스캔 결과:")
    print(f"  1단계 발견: {len(found_articles_1)}개")
    print(f"  2단계 추가 발견: {len(additional_articles)}개")
    print(f"  총 발견: {len(all_found_articles)}개")
    
    # 3단계: 커버리지 분석
    print(f"\n3️⃣ 3단계: 커버리지 분석")
    coverage_report = checker.analyze_coverage(all_found_articles)
    
    # 4단계: 결과 저장
    print(f"\n4️⃣ 4단계: 결과 저장")
    articles_file, coverage_file, json_file = checker.save_results(all_found_articles, coverage_report)
    
    print(f"\n✅ 분석 완료!")

if __name__ == "__main__":
    main() 