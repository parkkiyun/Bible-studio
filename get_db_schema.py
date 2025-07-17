import sqlite3

db_path = r"C:\Users\basar\Documents\Bible project\ai-sermon-assistant\src\data\bible.db"

def check_commentaries_data(db_path, book_name, chapter):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM commentaries WHERE book = ? AND chapter = ?;", (book_name, chapter))
        count = cursor.fetchone()[0]
        print(f"Number of commentaries for '{book_name}' chapter {chapter}: {count}")

        if count > 0:
            print(f"Sample data for '{book_name}' chapter {chapter} (first 5 rows):")
            cursor.execute("SELECT book, chapter, verse, commentary FROM commentaries WHERE book = ? AND chapter = ? LIMIT 5;", (book_name, chapter))
            for row in cursor.fetchall():
                print(row)
        else:
            print(f"No commentaries found for '{book_name}' chapter {chapter}.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_commentaries_data(db_path, '요한복음', 3)