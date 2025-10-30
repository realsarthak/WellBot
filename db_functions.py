import sqlite3
import bcrypt

def init_db():
    """Initializes the SQLite database and creates tables if they don't exist."""
    conn = sqlite3.connect('healthbot.sqlite', check_same_thread=False)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER,
            language TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(hashed_password, user_password):
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password)

def add_user(email, password):
    conn = sqlite3.connect('healthbot.sqlite', check_same_thread=False)
    c = conn.cursor()
    try:
        hashed = hash_password(password)
        c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed))
        user_id = c.lastrowid
        # Create a default profile upon registration
        c.execute("INSERT INTO profiles (user_id, name, language) VALUES (?, ?, ?)", (user_id, '', 'English'))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(email, password):
    conn = sqlite3.connect('healthbot.sqlite', check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT id, password FROM users WHERE email = ?", (email,))
    user_data = c.fetchone()
    conn.close()
    if user_data:
        user_id, hashed_password = user_data
        if check_password(hashed_password, password):
            return user_id
    return None

def get_profile(user_id):
    conn = sqlite3.connect('healthbot.sqlite', check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT name, age, language FROM profiles WHERE user_id = ?", (user_id,))
    profile = c.fetchone()
    conn.close()
    return profile

def update_profile(user_id, name, age, language):
    conn = sqlite3.connect('healthbot.sqlite', check_same_thread=False)
    c = conn.cursor()
    c.execute("UPDATE profiles SET name = ?, age = ?, language = ? WHERE user_id = ?", (name, age, language, user_id))
    conn.commit()
    conn.close()