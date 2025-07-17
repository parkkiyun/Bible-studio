import sqlite3
import json

def analyze_bible_database():
    """
    bible_database.db의 구조를 분석
    """
    try:
        conn = sqlite3.connect('bible_database.db')
        cursor = conn.cursor()
        
        print("=== Bible Database 구조 분석 ===\n")
        
        # 1. 테이블 목록 확인
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("📋 테이블 목록:")
        for table in tables:
            print(f"- {table[0]}")
        
        # 2. 각 테이블의 스키마 확인
        for table_name in [t[0] for t in tables]:
            print(f"\n🔍 테이블 '{table_name}' 스키마:")
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            for col in columns:
                col_id, name, data_type, not_null, default_val, primary_key = col
                pk_marker = " (PRIMARY KEY)" if primary_key else ""
                not_null_marker = " NOT NULL" if not_null else ""
                default_marker = f" DEFAULT {default_val}" if default_val else ""
                
                print(f"  {name}: {data_type}{pk_marker}{not_null_marker}{default_marker}")
            
            # 3. 데이터 샘플 확인
            print(f"\n📊 테이블 '{table_name}' 데이터 샘플:")
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"총 {count:,}개 레코드")
            
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                sample_data = cursor.fetchall()
                
                # 컬럼 이름 가져오기
                column_names = [description[0] for description in cursor.description]
                
                print("상위 5개 레코드:")
                for i, row in enumerate(sample_data, 1):
                    print(f"  레코드 {i}:")
                    for col_name, value in zip(column_names, row):
                        # 긴 텍스트는 짧게 표시
                        if isinstance(value, str) and len(value) > 100:
                            display_value = value[:100] + "..."
                        else:
                            display_value = value
                        print(f"    {col_name}: {display_value}")
                    print()
        
        # 4. 특정 성경책 데이터 구조 확인 (창세기 예시)
        print("🔍 창세기 데이터 구조 확인:")
        for table_name in [t[0] for t in tables]:
            try:
                # 성경이름이 포함된 컬럼 찾기
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                col_names = [col[1] for col in columns]
                
                # 성경 관련 컬럼 추정
                bible_col = None
                chapter_col = None
                verse_col = None
                content_col = None
                
                for col in col_names:
                    col_lower = col.lower()
                    if any(keyword in col_lower for keyword in ['book', '성경', 'bible']):
                        bible_col = col
                    elif any(keyword in col_lower for keyword in ['chapter', '장']):
                        chapter_col = col
                    elif any(keyword in col_lower for keyword in ['verse', '절']):
                        verse_col = col
                    elif any(keyword in col_lower for keyword in ['content', '내용', 'text']):
                        content_col = col
                
                if bible_col:
                    # 창세기 데이터 샘플 조회
                    cursor.execute(f"SELECT * FROM {table_name} WHERE {bible_col} LIKE '%창세기%' OR {bible_col} LIKE '%Genesis%' LIMIT 3")
                    genesis_data = cursor.fetchall()
                    
                    if genesis_data:
                        print(f"\n테이블 '{table_name}'의 창세기 데이터:")
                        column_names = [description[0] for description in cursor.description]
                        
                        for i, row in enumerate(genesis_data, 1):
                            print(f"  창세기 레코드 {i}:")
                            for col_name, value in zip(column_names, row):
                                if isinstance(value, str) and len(value) > 80:
                                    display_value = value[:80] + "..."
                                else:
                                    display_value = value
                                print(f"    {col_name}: {display_value}")
                            print()
                        break
            except Exception as e:
                continue
        
        # 5. 데이터베이스 요약 정보
        print("\n📈 데이터베이스 요약:")
        total_records = 0
        for table_name in [t[0] for t in tables]:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            total_records += count
            print(f"- {table_name}: {count:,}개 레코드")
        
        print(f"\n총 레코드 수: {total_records:,}개")
        
        conn.close()
        
        return {
            'tables': [t[0] for t in tables],
            'total_records': total_records
        }
        
    except Exception as e:
        print(f"오류 발생: {e}")
        return None

if __name__ == "__main__":
    analyze_bible_database() 