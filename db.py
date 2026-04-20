import sqlite3
from contextlib import closing

DB_NAME = "signal_feed.db"


# ---------------------------------
# Create fresh connection
# ---------------------------------
def get_connection():
    conn = sqlite3.connect(
        DB_NAME,
        timeout=30,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------
# Initialize DB
# WAL runs only once here
# ---------------------------------
def init_db():
    with closing(get_connection()) as conn:
        cursor = conn.cursor()

        cursor.execute("PRAGMA foreign_keys = ON;")

        # Try WAL once safely
        try:
            cursor.execute("PRAGMA journal_mode=WAL;")
        except:
            pass

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            source TEXT,
            url TEXT UNIQUE,
            category TEXT,
            published_at TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            city TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_interests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            interest TEXT,
            weight REAL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_sub_interests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            parent_interest TEXT,
            sub_interest TEXT,
            weight REAL
        )
        """)

        conn.commit()


# ---------------------------------
# Save Content Items
# Ignores duplicate URLs safely
# ---------------------------------
def save_items(items):
    with closing(get_connection()) as conn:
        cursor = conn.cursor()

        for item in items:
            try:
                category = item.get("category", "")

                if isinstance(category, list):
                    category = ", ".join(category)

                cursor.execute("""
                    INSERT OR IGNORE INTO content
                    (title, source, url, category, published_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    item.get("title"),
                    item.get("source"),
                    item.get("url"),
                    category,
                    item.get("published_at", "")
                ))

            except Exception as e:
                print("save_items error:", e, item)

        conn.commit()

# ---------------------------------
# Create User
# Returns inserted user id
# ---------------------------------
def create_user(name="New User", city="Unknown"):
    with closing(get_connection()) as conn:
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO users (name, city)
        VALUES (?, ?)
        """, (name, city))

        conn.commit()
        return cursor.lastrowid


# ---------------------------------
# Save Main Interest
# ---------------------------------
def save_interest(user_id, interest, weight):
    with closing(get_connection()) as conn:
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO user_interests
        (user_id, interest, weight)
        VALUES (?, ?, ?)
        """, (user_id, interest, weight))

        conn.commit()


# ---------------------------------
# Save Sub Interest
# ---------------------------------
def save_sub_interest(user_id, parent_interest, sub_interest, weight):
    with closing(get_connection()) as conn:
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO user_sub_interests
        (user_id, parent_interest, sub_interest, weight)
        VALUES (?, ?, ?, ?)
        """, (user_id, parent_interest, sub_interest, weight))

        conn.commit()


def get_unique_interest_keywords():
    """
    Fetch all unique interests + sub-interests
    Returns one clean Python list
    Useful for populating content table / feed queries
    """

    conn = get_connection()
    cursor = conn.cursor()

    # Main interests
    cursor.execute("""
        SELECT interest
        FROM user_interests
    """)
    interests = [row[0].strip().lower() for row in cursor.fetchall() if row[0]]

    # Sub interests
    cursor.execute("""
        SELECT sub_interest
        FROM user_sub_interests
    """)
    sub_interests = [row[0].strip().lower() for row in cursor.fetchall() if row[0]]

    conn.close()

    # Merge + remove duplicates
    combined = interests + sub_interests
    unique_keywords = sorted(list(set(combined)))

    return unique_keywords