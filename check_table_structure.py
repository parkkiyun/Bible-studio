import sqlite3

def check_table_structure():
    """commentaries 테이블 구조 확인"""
    db_path = 'bible_database.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 테이블 존재 여부 확인
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='commentaries'
        """)
        
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("commentaries 테이블이 존재합니다.")
            
            # 테이블 구조 확인
            cursor.execute("PRAGMA table_info(commentaries)")
            columns = cursor.fetchall()
            
            print("\n현재 테이블 구조:")
            for col in columns:
                print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
            
            # 샘플 데이터 확인
            cursor.execute("SELECT COUNT(*) FROM commentaries")
            count = cursor.fetchone()[0]
            print(f"\n현재 데이터 수: {count}개")
            
            if count > 0:
                cursor.execute("SELECT * FROM commentaries LIMIT 3")
                samples = cursor.fetchall()
                print("\n샘플 데이터:")
                for i, sample in enumerate(samples, 1):
                    print(f"  {i}: {sample}")
        else:
            print("commentaries 테이블이 존재하지 않습니다.")
    
    except Exception as e:
        print(f"오류 발생: {e}")
    
    finally:
        conn.close()

def fix_table_structure():
    """테이블 구조 수정"""
    db_path = 'bible_database.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("테이블 구조 수정 시작...")
        
        # 기존 테이블 백업
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS commentaries_backup AS 
            SELECT * FROM commentaries
        """)
        
        # 기존 테이블 삭제
        cursor.execute("DROP TABLE IF EXISTS commentaries")
        
        # 새 테이블 생성
        cursor.execute('''
            CREATE TABLE commentaries ( 
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                commentary_name TEXT,
                book_name TEXT,
                book_code TEXT,
                chapter INTEGER,
                verse INTEGER,
                text TEXT,
                version TEXT DEFAULT 'hochma',
                verse_title TEXT,
                article_id INTEGER,
                url TEXT,
                parsed_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 인덱스 생성
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_commentaries_book_chapter_verse 
            ON commentaries(book_name, chapter, verse)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_commentaries_article_id 
            ON commentaries(article_id)
        ''')
        
        # 백업 데이터가 있다면 복원 (가능한 컬럼만)
        cursor.execute("SELECT COUNT(*) FROM commentaries_backup")
        backup_count = cursor.fetchone()[0]
        
        if backup_count > 0:
            print(f"백업 데이터 {backup_count}개 복원 중...")
            
            # 공통 컬럼 확인
            cursor.execute("PRAGMA table_info(commentaries_backup)")
            backup_columns = [col[1] for col in cursor.fetchall()]
            
            cursor.execute("PRAGMA table_info(commentaries)")
            new_columns = [col[1] for col in cursor.fetchall()]
            
            # 공통 컬럼만 복원
            common_columns = [col for col in backup_columns if col in new_columns and col != 'id']
            
            if common_columns:
                columns_str = ', '.join(common_columns)
                cursor.execute(f"""
                    INSERT INTO commentaries ({columns_str})
                    SELECT {columns_str} FROM commentaries_backup
                """)
                print(f"  {len(common_columns)}개 컬럼 복원 완료")
        
        conn.commit()
        print("테이블 구조 수정 완료!")
        
        # 수정된 구조 확인
        cursor.execute("PRAGMA table_info(commentaries)")
        columns = cursor.fetchall()
        
        print("\n수정된 테이블 구조:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
    except Exception as e:
        conn.rollback()
        print(f"테이블 수정 실패: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("commentaries 테이블 구조 확인")
    print("=" * 50)
    
    check_table_structure()
    
    print("\n" + "=" * 50)
    response = input("테이블 구조를 수정하시겠습니까? (y/n): ")
    
    if response.lower() == 'y':
        fix_table_structure()
    else:
        print("취소되었습니다.")
