import sqlite3


DB_NAME = "library.db"


def get_connection():
    connection = sqlite3.connect(DB_NAME)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS authors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            country TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            genre TEXT NOT NULL,
            year INTEGER,
            author_id INTEGER NOT NULL,
            FOREIGN KEY (author_id)
                REFERENCES authors(id)
                ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            reader_name TEXT NOT NULL,
            loan_date TEXT NOT NULL,
            returned INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (book_id)
                REFERENCES books(id)
                ON DELETE CASCADE
        )
    """)

    connection.commit()
    connection.close()


def seed_db():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM loans")
    cursor.execute("DELETE FROM books")
    cursor.execute("DELETE FROM authors")

    cursor.executemany(
        """
        INSERT INTO authors (name, country)
        VALUES (?, ?)
        """,
        [
            ("Лев Толстой", "Russia"),
            ("J.K. Rowling", "United Kingdom"),
            ("Gabriel García Márquez", "Colombia"),
        ]
    )

    cursor.executemany(
        """
        INSERT INTO books (title, genre, year, author_id)
        VALUES (?, ?, ?, ?)
        """,
        [
            ("Война и мир", "classic", 1869, 1),
            ("Анна Каренина", "classic", 1878, 1),
            ("Harry Potter and the Philosopher's Stone", "fantasy", 1997, 2),
            ("Harry Potter and the Chamber of Secrets", "fantasy", 1998, 2),
            ("One Hundred Years of Solitude", "magic realism", 1967, 3),
            ("Love in the Time of Cholera", "romance", 1985, 3),
        ]
    )

    cursor.executemany(
        """
        INSERT INTO loans (book_id, reader_name, loan_date, returned)
        VALUES (?, ?, ?, ?)
        """,
        [
            (1, "Али", "2026-10-01", 1),
            (2, "Мухаммад", "2026-10-02", 0),
            (3, "Азиз", "2026-10-03", 0),
            (5, "Саид", "2026-10-04", 1),
        ]
    )

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_tables()
    seed_db()
    print("Database created and seeded successfully!")

