import sqlite3
import string
import Messages as msg

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
    
    try: 
        cursor.execute('''
            INSERT INTO users (name, email, username, password)
            VALUES (?,?,?,?)
        ''', (name, email, username, password))
        
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
            if key == password: 
                return "True", msg.MESSAGES["WELCOME_CLIENT"].format(user=name)
        
        return "False", msg.MESSAGES["AUTH_FAILED"]

    finally: 
        conn.close()
