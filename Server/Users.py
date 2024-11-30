import sqlite3
import string
import Messages as msg
import bcrypt 
import re

# ASCII upper and lower + '_@$&'
valid = list(string.ascii_letters + string.digits)
valid += ['_', '@', '$', '&']

# Creates the db if it doesn't exist yet
def create(DB): 
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
            name TEXT NOT NULL, 
            email TEXT NOT NULL, 
            username TEXT PRIMARY KEY, 
            password TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# Adds a user to the db
# Users are defined by their username
def add_user(DB, name, email, username, password):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    # Validate username characters
    for character in username: 
        if character not in valid: 
            return False, msg.MESSAGES["INVALID_USERNAME"]
    
    if not validate_email(email):
        return "False", "Invalid email format."

    try: 
        hashed_password = hash_password(password)
        cursor.execute('''
            INSERT INTO users (name, email, username, password)
            VALUES (?,?,?,?)''', (name, email, username, hashed_password))
        
        conn.commit()
        return "True", msg.MESSAGES["USER_ADDED_SUCCESS"].format(username=username)

    except sqlite3.IntegrityError:
        return "False", msg.MESSAGES["USERNAME_EXISTS"].format(username=username)
    
    finally: 
        conn.close()

# Authenticate user by checking username and password
def authenticate(DB, username, password): 

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    try: 
        cursor.execute('''
            SELECT name, password FROM users WHERE username = ?
        ''', (username,))
        result = cursor.fetchone()

        if result: 
            name, key = result
            if verify_password(key, password):
                return "True", msg.MESSAGES["WELCOME_CLIENT"].format(user=name)

        return "False", msg.MESSAGES["AUTH_FAILED"]

    finally: 
        conn.close()

#These two are self explainatory
#Uses bcrypt to encrypt passwords
def hash_password(password): 
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(stored_pass, given_pass): 
    return bcrypt.checkpw(given_pass.encode('utf-8'), stored_pass.encode('utf-8'))

#validates email format using regex
#I just wanted to flex my newly acquired regex knowledge
def validate_email(email): 
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

def search_user(DB, query): 
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    try:
        query = f"%{query}%"
        cursor.execute('SELECT username, email FROM users WHERE username LIKE ? OR email LIKE ?', (query, query))
        results = cursor.fetchall()
        if results:
            return [{"username": row[0], "email": row[1]} for row in results]
        return "No users found."
    finally:
        conn.close()

def delete_user(DB, username):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM users WHERE username = ?', (username,))
        conn.commit()
        return f"User '{username}' deleted successfully."
    except Exception as e:
        return f"Error deleting user: {e}"
    finally:
        conn.close()
