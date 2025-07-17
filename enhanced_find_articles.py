import requests
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime

def enhanced_find_articles():
    """발견된 범위를 기준으로 정밀 검색"""
    
    base_url = "https://nocr.net"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print("🔍 호크마 게시글 정밀 검색...")
    
    all_ids = set()
    
    # 발견된 범위: 139800 ~ 148500
    # 이 범위를 더 세밀하게 검색
    
    search_ranges = [
        (139000, 150000, 1),  # 139000~150000을 1씩 증가하며 전체 검색
    ]
    
    for start, end, step in search_ranges:
        print(f"\n📊 정밀 검색: {start}~{end} (step={step})")
        
        valid_count = 0
        consecutive_fails = 0
        
        for article_id in range(start, end, step):
            url = f"{base_url}/com_kor_hochma/{article_id}"
            
            try:
                response = requests.get(url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title_tag = soup.find('title')
                    
                    if title_tag:
                        title_text = title_tag.get_text()
                        # 호크마 주석인지 확인
                        if '주석' in title_text and any(book in title_text for book in 
                            ['창세기', '출애굽기', '레위기', '민수기', '신명기', '여호수아', '사사기', 
                             '룻기', '사무엘', '열왕기', '역대', '에스라', '느헤미야', '에스더', 
                             '욥기', '시편', '잠언', '전도서', '아가', '이사야', '예레미야', '에스겔', 
                             '다니엘', '호세아', '요엘', '아모스', '오바댜', '요나', '미가', '나훔', 
                             '하박국', '스바냐', '학개', '스가랴', '말라기', '마태', '마가', '누가', 
                             '요한', '사도행전', '로마서', '고린도', '갈라디아', '에베소', '빌립보', 
                             '골로새', '데살로니가', '디모데', '디도', '빌레몬', '히브리서', '야고보', 
                             '베드로', '유다', '계시록']):
                            
                            all_ids.add(article_id)
                            valid_count += 1
                            consecutive_fails = 0
                            print(f"✓ {article_id}: {title_text[:60]}...")
                        else:
                            consecutive_fails += 1
                    else:
                        consecutive_fails += 1
                else:
                    consecutive_fails += 1
                    
            except Exception as e:
                consecutive_fails += 1
            
            # 진행 상황 출력
            if article_id % 1000 == 0:
                print(f"  진행: {article_id} (발견: {valid_count}개, 연속실패: {consecutive_fails})")
            
            # 연속 500회 실패시 종료 (빈 구간으로 판단)
            if consecutive_fails >= 500:
                print(f"  연속 실패 500회, 검색 중단")
                break
            
            # 서버 부하 방지
            time.sleep(0.05)
    
    # 결과 정리
    final_ids = sorted(list(all_ids))
    
    print(f"\n🎉 정밀 검색 결과:")
    print(f"  총 {len(final_ids)}개 게시글 발견")
    if final_ids:
        print(f"  ID 범위: {min(final_ids)} ~ {max(final_ids)}")
    
    # JSON 파일로 저장
    result = {
        'scan_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_count': len(final_ids),
        'article_ids': final_ids,
        'id_range': {
            'min': min(final_ids) if final_ids else 0,
            'max': max(final_ids) if final_ids else 0
        }
    }
    
    json_filename = f"hochma_complete_ids_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"  저장: {json_filename}")
    
    # ID 목록도 출력
    print(f"\n📋 발견된 게시글 ID 목록:")
    for i, article_id in enumerate(final_ids):
        if i % 10 == 0 and i > 0:
            print()
        print(f"{article_id:6d}", end="  ")
    print()
    
    return final_ids

if __name__ == "__main__":
    article_ids = enhanced_find_articles() 