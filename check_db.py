import sqlite3

db_path = 'bible_database.db'

def check_commentaries_table():
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if commentaries table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='commentaries';")
        if cursor.fetchone():
            print("Table 'commentaries' exists.")
            
            # Check for data in commentaries table for John 3
            cursor.execute("SELECT COUNT(*) FROM commentaries WHERE book_name = '요한복음' AND chapter = 3;")
            count = cursor.fetchone()[0]
            print(f"Number of commentaries for '요한복음' chapter 3: {count}")

            if count > 0:
                print("Sample data for '요한복음' chapter 3:")
                cursor.execute("SELECT book_name, chapter, verse, text FROM commentaries WHERE book_name = '요한복음' AND chapter = 3 LIMIT 5;")
                for row in cursor.fetchall():
                    print(row)
            else:
                print("No commentaries found for '요한복음' chapter 3.")

        else:
            print("Table 'commentaries' does NOT exist.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_commentaries_table()
