# schema_creation.py
import sqlite3
import os

# Define the SQL as a module-level variable
create_tables_sql = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    email TEXT,
    join_date DATE DEFAULT CURRENT_DATE,
    profile_picture TEXT,
    bio TEXT
);

CREATE TABLE IF NOT EXISTS articles (
    article_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    contents TEXT,
    author_name TEXT,
    publication_date DATE,
    overall_rating REAL DEFAULT 0,
    is_fake BOOLEAN DEFAULT 0,
    submitter_id INT,
    ml_score REAL DEFAULT 0,
    source_link TEXT
);

CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS article_category (
    article_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    PRIMARY KEY (article_id, category_id),
    FOREIGN KEY(article_id) REFERENCES articles(article_id) ON DELETE CASCADE,
    FOREIGN KEY(category_id) REFERENCES categories(category_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ratings (
    rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    article_id INTEGER NOT NULL,
    rating_value INTEGER NOT NULL,
    comment TEXT,
    rating_date DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(article_id) REFERENCES articles(article_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_ratings_value ON ratings(rating_value);
CREATE INDEX IF NOT EXISTS idx_articles_title ON articles(title);

-- Trigger: Update overall_rating after each new rating
CREATE TRIGGER IF NOT EXISTS trg_update_overall_rating
AFTER INSERT ON ratings
BEGIN
    UPDATE articles
    SET overall_rating = (
        SELECT AVG(r.rating_value)
        FROM ratings r
        WHERE r.article_id = NEW.article_id
    )
    WHERE article_id = NEW.article_id;
END;
"""

def init_db():
    """Initialize the database with the schema"""
    # Get the directory where the current file is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, 'unfake.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.executescript(create_tables_sql)
    conn.commit()
    
    # Clean up duplicate categories
    cleanup_duplicates_sql = """
    DELETE FROM categories
    WHERE rowid NOT IN (
        SELECT MIN(rowid)
        FROM categories
        GROUP BY category_name
    );
    """
    cursor.execute(cleanup_duplicates_sql)
    conn.commit()
    
    print("Database initialized successfully!")
    conn.close()

if __name__ == "__main__":
    init_db()
