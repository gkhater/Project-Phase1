import sqlite3
import Messages as msg

def create(DB): 
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            seller TEXT NOT NULL,
            count INTEGER DEFAULT 1,  -- Initialized to 1
            buyer TEXT DEFAULT 'N/A',  -- Initialized to 'N/A'
            FOREIGN KEY (seller) REFERENCES users(username)
        )
    ''')

    conn.commit()
    conn.close()

def buy(DB, product_id, username): 
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON")

    try: 
        cursor.execute("SELECT name, price, count FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()

        if product:
            name, price, count = product

            if count > 0:
                cursor.execute("UPDATE products SET count = 0, buyer = ? WHERE id = ?", (username, product_id))
                conn.commit()

                return msg.MESSAGES['SALE_SUCCESS'].format(name=name, price=price)
            else:
                return msg.MESSAGES['ITEM_NOT_AVAILABLE'].format(name=name)
        else: 
            return msg.MESSAGES['PRODUCT_NOT_FOUND']
        
    except Exception as e: 
        return f"Error processing purchase: {e}"
    
    finally: 
        conn.close()

def view_sold(DB, seller_username):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT name, price, buyer FROM products WHERE seller = ? AND buyer != 'N/A'", (seller_username,))
        sold_products = cursor.fetchall()

        if sold_products:
            result = "Products you've sold:\n"
            for product in sold_products:
                name, price, buyer = product
                result += f"Product: {name}, Price: ${price}, Buyer: {buyer}\n"
            return result
        else:
            return msg.MESSAGES['NO_SALES']

    except Exception as e:
        return f"Error fetching sold products: {e}"

    finally:
        conn.close()

def add(DB, product_name, username, price, description): 
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    
    try: 
        cursor.execute('''
            INSERT INTO products (name, description, price, seller)
            VALUES (?, ?, ?, ?)
        ''', (product_name, description, price, username))
        conn.commit()

        return msg.MESSAGES['PRODUCT_ADDED'].format(product_name = product_name)
    
    except Exception as e: 
        return f"Error adding product {e}"

    finally: 
        conn.close()

def fetch_products(DB):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute('SELECT id, name, description, price, seller FROM products WHERE count > 0')
    products = cursor.fetchall()

    conn.close()
    return products