from corrected_bulk_parser import CorrectedHochmaParser

def main():
    """테스트용 메인 함수"""
    print("🧪 수정된 파서 테스트")
    print("=" * 40)
    
    # 테스트할 게시글 ID들
    test_articles = [139393, 139395, 139477, 141000, 139453]
    
    parser = CorrectedHochmaParser()
    
    all_data = []
    
    for article_id in test_articles:
        print(f"\n📋 게시글 {article_id} 테스트...")
        
        # 제목 추출 테스트
        title, commentary_name, book_name, chapter = parser.extract_title_and_info(article_id)
        print(f"  제목: {title}")
        print(f"  주석명: {commentary_name}")
        print(f"  성경책: {book_name}")
        print(f"  장: {chapter}")
        
        # 내용 파싱 테스트
        verses_data = parser.parse_article_content(article_id)
        
        if verses_data:
            print(f"  파싱된 절 수: {len(verses_data)}")
            print(f"  첫 번째 절: {verses_data[0]['verse']}절")
            print(f"  마지막 절: {verses_data[-1]['verse']}절")
            print(f"  내용 샘플: {verses_data[0]['content'][:100]}...")
            all_data.extend(verses_data)
        else:
            print(f"  ❌ 파싱 실패")
    
    if all_data:
        print(f"\n📊 전체 테스트 결과:")
        print(f"  총 절 수: {len(all_data)}")
        
        # 성경책별 통계
        books = {}
        for item in all_data:
            book = item['book_name']
            if book not in books:
                books[book] = {'chapters': set(), 'verses': 0}
            books[book]['chapters'].add(item['chapter'])
            books[book]['verses'] += 1
        
        print(f"  성경책별 요약:")
        for book, stats in books.items():
            chapters = sorted(stats['chapters'])
            print(f"    {book}: {len(chapters)}장 ({min(chapters)}~{max(chapters)}), {stats['verses']}절")
        
        # 간단한 엑셀 저장
        filename = parser.save_to_excel(all_data, "test_corrected_parsing.xlsx")
        print(f"\n💾 테스트 결과 저장: {filename}")
    
    else:
        print("❌ 테스트 실패 - 파싱된 데이터가 없습니다.")

if __name__ == "__main__":
    main() 