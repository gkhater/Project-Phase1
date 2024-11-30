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
            count INTEGER DEFAULT 1,  
            buyer TEXT DEFAULT 'N/A',  
            rating REAL DEFAULT 0.0,
            rating_count INTEGER DEFAULT 0,
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
                newcount = count - 1
                cursor.execute("UPDATE products SET count = ?, buyer = ? WHERE id = ?", (newcount, username, product_id))
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

def update_product(DB, product_id, price=None, description=None, count=None):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    try:
        if price:
            cursor.execute('UPDATE products SET price = ? WHERE id = ?', (price, product_id))
        if description:
            cursor.execute('UPDATE products SET description = ? WHERE id = ?', (description, product_id))
        if count is not None:
            cursor.execute('UPDATE products SET count = ? WHERE id = ?', (count, product_id))
        conn.commit()
        return "Product updated successfully."
    except Exception as e:
        return f"Error updating product: {e}"
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

def add(DB, product_name, username, price, description, count = 1): 
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    
    try: 
        cursor.execute('''
            INSERT INTO products (name, description, price, seller, count)
            VALUES (?, ?, ?, ?, ?)
        ''', (product_name, description, price, username, count))
        conn.commit()

        ID = cursor.lastrowid
        return msg.MESSAGES['PRODUCT_ADDED'].format(product_name = product_name), ID
    
    except Exception as e: 
        return f"Error adding product {e}"

    finally: 
        conn.close()

def rate_product(DB, product_id, rating): 
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    try: 
        cursor.execute('SELECT rating, rating_count FROM products WHERE id = ?', (product_id,))
        product = cursor.fetchone()

        if product: 
            current_rating, count = product
            new_count = count + 1
            new_rating = (current_rating * count + rating) / new_count

            cursor.execute('UPDATE products SET rating = ?, rating_count = ? WHERE id = ?', 
                           (new_rating, new_count, product_id))
            conn.commit()
            return msg.MESSAGES['RATING_SUCCESS'].format(name=product_id, rating=rating)
        else: 
            return msg.MESSAGES['PRODUCT_NOT_FOUND']
    except Exception as e:
        return f"Error rating product: {e}"
    finally: 
        conn.close()

def search_products(DB, query): 
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    try:
        query = f"%{query}%"
        cursor.execute('SELECT id, name, description, price, seller FROM products WHERE (name LIKE ? OR description LIKE ?) AND count > 0',
                       (query, query))
        results = cursor.fetchall()
        if results:
            return results
        else:
            return msg.MESSAGES['NO_SEARCH_RESULTS'].format(query=query)
    except Exception as e:
        return f"Error searching products: {e}"
    finally:
        conn.close()

def notify_seller(DB, product_id): 
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT seller, name FROM products WHERE id = ?', (product_id,))
        product = cursor.fetchone()

        if product:
            seller, name = product
            return msg.MESSAGES['NOTIFY_NEW_PRODUCT'].format(name=name, owner=seller)
        else:
            return 
    except Exception as e:
        return f"Error notifying seller: {e}"
    finally:
        conn.close()

def fetch_products(DB):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute('SELECT id, name, description, price, seller, rating, rating_count FROM products WHERE count > 0')
    products = cursor.fetchall()

    conn.close()
    return products

def fetch_product(DB, product_id): 
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT id, name, description, price, seller, rating, rating_count FROM products WHERE id = ?', (product_id,))
        return cursor.fetchone()
    finally:
        conn.close()