import sqlite3
import string
import Messages as msg
import bcrypt 
import re
from Rates import convert

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
            password TEXT NOT NULL, 
            balance INTEGER DEFAULT 0, 
            currency TEXT DEFAULT USD
        )
    ''')

    conn.commit()
    conn.close()

# Adds a user to the db
# Users are defined by their username
#TODO
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
                return "True", name

        return "False", ""

    finally: 
        conn.close()

def deposit(DB, username, amount): 
    
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    try: 
        cursor.execute("SELECT balance, currency FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()

        if result: 
            current_balance, currency = result[0], result[1]
            new_balance = current_balance + amount
            print(new_balance + "YOU ARE NOW POOR")
            cursor.execute("UPDATE users SET balance = ? WHERE username = ?", (new_balance, username))
            conn.commit()
            return {
                "code": 200, 
                "username": username,
                "balance": new_balance
            }
        else:
            return { 
                "code": 404, 
                "error": f"{username} not found"
            }
    finally: 
        conn.close()

def get_balance(DB, username): 
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    try: 
        cursor.execute("SELECT balance, currency FROM users WHERE username = ? ", (username,))
        result = cursor.fetchone()

        if result: 
            return{
                "code": 200, 
                "balance": result[0] * convert('USD',result[1])
            } 
        else: 
            return { 
                "code": 404, 
                "error": f"{username} not found."
            }
    finally: 
        conn.close()

def get_currency(DB, username): 
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    try: 
        cursor.execute("SELECT currency FROM users WHERE username = ? ", (username,))
        result = cursor.fetchone()

        if result: 
            return result[0]
        else: 
            return "USD"
    finally: 
        conn.close()

def set_currency(DB, username, new_currency):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    try:
        # Validate the new currency (assuming a list of valid currency codes)
        valid_currencies = ["USD", "EUR", "GBP", "JPY", "AUD"]  # Add more as needed
        if new_currency not in valid_currencies:
            return f"Invalid currency '{new_currency}'. Valid options are: {', '.join(valid_currencies)}."

        # Check if user exists
        cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
        if not cursor.fetchone():
            return f"User with username '{username}' not found."

        # Update the currency
        cursor.execute("UPDATE users SET currency = ? WHERE username = ?", (new_currency, username))
        conn.commit()
        return {
            "code": 200,
            "currency": new_currency
        }
    except Exception as e:
        return {
            "code": 500, 
            "error": "Internal Server error."
        }
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
