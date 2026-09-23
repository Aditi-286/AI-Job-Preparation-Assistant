import sqlite3

DATABASE = "database.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_database():

    connection = get_connection()
    cursor = connection.cursor()

    # USERS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            target_job TEXT,
            skills TEXT,
            education TEXT
        )
    """)

    # PROGRESS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            dsa INTEGER DEFAULT 0,
            python INTEGER DEFAULT 0,
            sql INTEGER DEFAULT 0,
            oop INTEGER DEFAULT 0,
            dbms INTEGER DEFAULT 0,
            projects INTEGER DEFAULT 0,
            interview INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # PREPARATION PLANS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            plan TEXT,
            skill_gap TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # INTERVIEW HISTORY
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            question TEXT,
            answer TEXT,
            feedback TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    connection.commit()
    connection.close()


def create_progress(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO progress (user_id)
        VALUES (?)
    """, (user_id,))

    connection.commit()
    connection.close()


if __name__ == "__main__":

    create_database()

    print("Database created successfully!")