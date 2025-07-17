from excel_hochma_parser import ExcelHochmaParser

def test_range_excel():
    """범위 파싱 테스트 - 창세기 29~31장"""
    parser = ExcelHochmaParser()
    
    # 창세기 29~31장 (139475~139477) 테스트
    start_id = 139475  # 창세기 30장
    end_id = 139477    # 창세기 31장
    
    print(f"범위 테스트: 창세기 30~31장 (ID: {start_id}~{end_id})")
    
    # 엑셀 파일로 저장
    result = parser.parse_range_to_excel(
        start_id=start_id, 
        end_id=end_id, 
        excel_filename="창세기_30_31장_테스트.xlsx",
        delay=1  # 1초 지연
    )
    
    if result:
        print(f"\n✓ 범위 엑셀 파일 생성 성공!")
        print(f"  파일명: {result['excel_file']}")
        print(f"  파싱된 게시글: {result['parsed_count']}개")
        print(f"  전체 절 수: {len(result['dataframe'])}")
        
        # 성경책별 요약
        book_summary = result['dataframe'].groupby('성경책').agg({
            '장': ['min', 'max', 'nunique'],
            '절': 'count',
            '내용_길이': 'mean'
        }).round(1)
        
        print(f"\n📊 성경책별 요약:")
        for book in book_summary.index:
            min_ch = book_summary.loc[book, ('장', 'min')]
            max_ch = book_summary.loc[book, ('장', 'max')]
            ch_count = book_summary.loc[book, ('장', 'nunique')]
            verse_count = book_summary.loc[book, ('절', 'count')]
            avg_length = book_summary.loc[book, ('내용_길이', 'mean')]
            
            print(f"  - {book}: {min_ch}~{max_ch}장 ({ch_count}개 장, {verse_count}개 절, 평균 {avg_length:.0f}자)")
        
        return result['excel_file']
    else:
        print("✗ 범위 엑셀 파일 생성 실패")
        return None

if __name__ == "__main__":
    test_range_excel() 