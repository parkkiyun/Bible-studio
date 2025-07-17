import requests
from bs4 import BeautifulSoup
import re
import time
import json
from datetime import datetime

def find_all_article_ids():
    """호크마 사이트에서 모든 6자리 게시글 ID 찾기"""
    
    base_url = "https://nocr.net"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print("🔍 호크마 사이트에서 게시글 ID 수집 중...")
    
    all_ids = set()
    
    # 방법 1: 범위 기반 스캔 (기존에 본 ID들 기준)
    print("\n📊 범위 기반 스캔...")
    known_ids = [139393, 139453, 139475, 139477]  # 알려진 ID들
    
    # 최소/최대값 추정
    min_id = min(known_ids) - 100
    max_id = max(known_ids) + 100
    
    print(f"스캔 범위: {min_id} ~ {max_id}")
    
    valid_ids = []
    failed_count = 0
    
    for article_id in range(min_id, max_id + 1):
        url = f"{base_url}/com_kor_hochma/{article_id}"
        
        try:
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                # 실제 호크마 주석 페이지인지 확인
                soup = BeautifulSoup(response.text, 'html.parser')
                title_tag = soup.find('title')
                
                if title_tag:
                    title_text = title_tag.get_text()
                    if '주석' in title_text and any(book in title_text for book in 
                        ['창세기', '출애굽기', '레위기', '민수기', '신명기', '여호수아', '사사기', 
                         '룻기', '사무엘', '열왕기', '역대', '에스라', '느헤미야', '에스더', 
                         '욥기', '시편', '잠언', '전도서', '아가', '이사야', '예레미야', '에스겔', 
                         '다니엘', '호세아', '요엘', '아모스', '오바댜', '요나', '미가', '나훔', 
                         '하박국', '스바냐', '학개', '스가랴', '말라기', '마태', '마가', '누가', 
                         '요한', '사도행전', '로마서', '고린도', '갈라디아', '에베소', '빌립보', 
                         '골로새', '데살로니가', '디모데', '디도', '빌레몬', '히브리서', '야고보', 
                         '베드로', '유다', '계시록']):
                        valid_ids.append(article_id)
                        all_ids.add(article_id)
                        print(f"✓ {article_id}: {title_text[:50]}...")
                        failed_count = 0
                    else:
                        failed_count += 1
                else:
                    failed_count += 1
            else:
                failed_count += 1
                
        except Exception as e:
            failed_count += 1
            
        # 연속 실패 시 범위 확장 중단
        if failed_count > 20:
            print(f"  연속 실패 20회, 범위 스캔 중단")
            break
            
        # 서버 부하 방지
        time.sleep(0.1)
        
        if article_id % 50 == 0:
            print(f"  진행: {article_id} (발견: {len(valid_ids)}개)")
    
    print(f"\n📋 범위 스캔 결과: {len(valid_ids)}개 게시글 발견")
    
    # 방법 2: 더 넓은 범위로 샘플링
    print(f"\n🎯 확장 샘플링...")
    
    # 6자리 ID 범위에서 샘플링 (100000~999999)
    sample_ranges = [
        (100000, 110000, 1000),  # 10만대, 1000개씩 점프
        (130000, 150000, 100),   # 13-15만대, 100개씩 점프 (알려진 범위 근처)
        (200000, 210000, 1000),  # 20만대
        (500000, 510000, 1000),  # 50만대
    ]
    
    for start, end, step in sample_ranges:
        print(f"  샘플링: {start}~{end} (step={step})")
        sample_count = 0
        
        for article_id in range(start, end, step):
            url = f"{base_url}/com_kor_hochma/{article_id}"
            
            try:
                response = requests.get(url, headers=headers, timeout=3)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title_tag = soup.find('title')
                    
                    if title_tag and '주석' in title_tag.get_text():
                        if article_id not in all_ids:
                            all_ids.add(article_id)
                            print(f"    ✓ {article_id}: 새 게시글 발견")
                            sample_count += 1
                            
            except:
                pass
                
            time.sleep(0.05)  # 빠른 샘플링
            
        print(f"    → {sample_count}개 추가 발견")
    
    # 결과 정리
    final_ids = sorted(list(all_ids))
    
    print(f"\n🎉 최종 결과:")
    print(f"  총 {len(final_ids)}개 게시글 발견")
    print(f"  ID 범위: {min(final_ids)} ~ {max(final_ids)}")
    
    # JSON 파일로 저장
    result = {
        'scan_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_count': len(final_ids),
        'article_ids': final_ids,
        'id_range': {
            'min': min(final_ids),
            'max': max(final_ids)
        }
    }
    
    json_filename = f"hochma_article_ids_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"  저장: {json_filename}")
    
    return final_ids

if __name__ == "__main__":
    article_ids = find_all_article_ids() 