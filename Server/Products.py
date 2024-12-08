import sqlite3
import Messages as msg
import Users 
import json
from Rates import convert

def create(DB): 
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            image TEXT,
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

def get_seller(DB, product_id): 
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT seller FROM products WHERE id = ?", (product_id,))
        result = cursor.fetchone()

        if result: 
            return result[0]
        else: 
            return f"Product with ID {product_id} not found."
        
    finally: 
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

            if count < 0:
                data = {
                    "code": 400, 
                    "error": "Item not available."
                }
                json_data = json.dumps(data, indent=4)
                return json_data
            if price > Users.get_balance(DB, username)["balance"]: 
                data = {
                    "code": 400, 
                    "error": "Insuficient funds."
                }
                json_data = json.dumps(data, indent=4)
                return json_data
            
            Users.deposit(DB, username, -price)
            seller = get_seller(DB, product_id)
            Users.deposit(DB, seller, price)
            newcount = count - 1
            cursor.execute("UPDATE products SET count = ?, buyer = ? WHERE id = ?", (newcount, username, product_id))
            conn.commit()

            data = { 
                "code": 200, 
                "name": name, 
                "price": price
            }              
            
        else: 
            data = { 
                "code": 404, 
                "error": "Product not found"
            }
        
        json_data = json.dumps(data, indent=4)
        return json_data
        
    except Exception as e: 
        return f"Error processing purchase: {e}"
    
    finally: 
        conn.close()

def update_product(DB, product_id, username, price=None, description=None, count=None, image = None):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    currency = Users.get_currency(DB, username)

    try:
        if price:
            price = price * convert(currency, 'USD')
            cursor.execute('UPDATE products SET price = ? WHERE id = ?', (price, product_id))
        if description:
            cursor.execute('UPDATE products SET description = ? WHERE id = ?', (description, product_id))
        if count is not None:
            cursor.execute('UPDATE products SET count = ? WHERE id = ?', (count, product_id))
        if image is not None:
            cursor.execute('UPDATE products SET image = ? WHERE id = ?', (image, product_id))
        conn.commit()
        return "Product updated successfully."
    except Exception as e:
        return f"Error updating product."
    finally:
        conn.close()

def view_sold(DB, seller_username, username):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT name, price, buyer FROM products WHERE seller = ? AND buyer != 'N/A'", (seller_username,))
        sold_products = cursor.fetchall()

        currency = Users.get_currency(DB, username)
        if sold_products:
            result = []
            for product in sold_products:
                name, price, buyer = product
                result.append({
                    "Product": name,
                    "Price": price * convert("USD", currency),
                    "Buyer": buyer
                })

            data = {
                "code": 200, 
                "result": result
            }
        else:
            data = { 
                "code": 404, 
                "error": "No sale"
            }

        json_data = json.dumps(data, indent=4)
        return json_data

    except Exception as e:
        return f"Error fetching sold products: {e}"

    finally:
        conn.close()

def add(DB, product_name, username, price, description, image, count = 1): 
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    
    currency = Users.get_currency(DB, username)
    try: 
        rate = convert(currency, 'USD')
        price = float(price) * float(rate)

        cursor.execute('''
            INSERT INTO products (name, description, price, seller, count, image)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (product_name, description, price, username, count, image))
        conn.commit()

        ID = cursor.lastrowid
        print(ID)

        data = { 
            "code": 200, 
            "product_name": product_name, 
            "description": description, 
            "price": price, 
            "username": username, 
            "count": count
        }
        return data, ID
    
    except Exception as e: 
        data = {
            "code": 500, 
            "error": f"Internal error adding product {e}"
        }
        return data, 0

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

            data = {
                "code": 200, 
                "rating": rating
            }
        else: 
            data = {
                "code": 404, 
                "error": "Product Not found."
            }
        
        return data
    except Exception as e:
        return f"Error rating product: {e}"
    finally: 
        conn.close()

def search_products(DB, query): 
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    try:
        query = f"%{query}%"
        cursor.execute('SELECT id, name, count, description, price, seller, rating, rating_count, image FROM products WHERE (name LIKE ? OR description LIKE ?) AND count > 0',
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

    cursor.execute('SELECT id, name, count, description, price, seller, rating, rating_count, image FROM products WHERE count > 0')
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