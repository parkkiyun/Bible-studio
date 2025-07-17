from hochma_parser import HochmaParser

def test_parser():
    parser = HochmaParser()
    
    # 테스트할 게시글 ID들
    test_ids = ['139393', '139475', '139477']  # 창세기 1장, 30장, 31장
    
    for article_id in test_ids:
        print(f"\n{'='*60}")
        print(f"게시글 ID: {article_id} 테스트")
        print('='*60)
        
        result = parser.parse_single_article(article_id)
        
        if result:
            print(f"제목: {result['title']}")
            print(f"성경책: {result['book_name']} {result['chapter']}장")
            print(f"본문 길이: {len(result['content'])}자")
            print(f"본문 시작 200자:")
            print(result['content'][:200])
            print("...")
        else:
            print("파싱 실패")

if __name__ == "__main__":
    test_parser() 