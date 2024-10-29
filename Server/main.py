import socket
import threading
import Users as users
import Products as Products
import Messages as msg

DB = 'auboutique.db'

online_users = {}

def get_users(): 
    return '\n\t'.join(online_users.keys())

def get_products(): 
    return '\n'.join([f"ID: {product[0]}, Name: {product[1]}, Description: {product[2]}, Price: {product[3]}, Seller: {product[4]}" 
                      for product in Products.fetch_products(DB)])

def is_online(username): 
    if username in online_users: 
        return msg.MESSAGES['USER_ONLINE'].format(username=username)
    return msg.MESSAGES['USER_OFFLINE'].format(username=username)

def handle_client(client_socket, username):

    products = get_products()
    users_list = get_users()

    # Format prompt message
    client_socket.send((msg.MESSAGES['PROMPT_USER'].format(items=products, users=users_list)).encode())

    try:
        while True: 
            response = client_socket.recv(1024).decode()
            response = response.split(' ') 

            if response[0].upper() == "LOGOUT": 
                client_socket.send(msg.MESSAGES["LOGOUT"].encode())
                break
            if response[0].upper() == "TEXT": 
                destination, message = response[1], " ".join(response[2:])
                client_socket.send(send_Message(username, destination, message).encode())
            elif response[0].upper() == "HELPME": 
                client_socket.send(msg.MESSAGES["HELP_PROMPT"].encode())
            elif response[0].upper() == "CHECK":
                if len(response) > 1:  
                    ans = is_online(response[1])
                    client_socket.send(ans.encode())
                else:
                    client_socket.send(msg.MESSAGES['INVALID_CHECK'].encode())
            elif response[0].upper() == "PRODUCTS": 
                products = "Available products: \n" + get_products()
                client_socket.send(products.encode())
            elif response[0].upper() == "BUY":
                if len(response) > 1:
                    product_id = response[1].strip()  
                    result = Products.buy(DB, product_id, username)  
                    client_socket.send(result.encode())
                else:
                    client_socket.send(msg.MESSAGES['INVALID_BUY'].encode())
            elif response[0].upper() == "ADD":                 
                if len(response) > 3: 
                    name, price, description = response[1].strip(), response[2].strip(), response[3].strip()
                    result = Products.add(DB, name, username, price, description)
                    client_socket.send(result.encode())
                else: 
                    message = msg.MESSAGES['INVALID_ADD']
                    client_socket.send(message.encode())
            elif response[0].upper() == "SOLD": 
                result = Products.view_sold(DB, username)
                client_socket.send(result.encode())
            elif response[0].upper() == "ONLINE": 
                users_list = get_users()
                message = f'''Online users: \n {users_list}'''
                client_socket.send(message.encode())
            else: 
                client_socket.send(msg.MESSAGES["UNKNOWN_COMMAND"].encode())
    
    finally:
        if username in online_users: 
            del online_users[username] 
            print(msg.MESSAGES['USER_DISCONNECTED'])

        client_socket.close()

def send_Message(username, destination, message): 
    if destination not in online_users: 
        return msg.MESSAGES["TEXT_OFFLINE"].format(destination=destination)
    
    destination_socket = online_users[destination]
    message = f"[From {username}] {message}"
    destination_socket.send(message.encode())
    return msg.MESSAGES["TEXT_SUCCESS"].format(destination=destination)

def signOn_client(client_socket): 
    try:
        while True: 
            client_socket.send(msg.MESSAGES["WELCOME_PROMPT"].encode())  
            choice = client_socket.recv(1024).decode()

            if choice.upper() == 'S': 
                name = client_socket.recv(1024).decode()

                email = client_socket.recv(1024).decode()

                username = client_socket.recv(1024).decode()

                password = client_socket.recv(1024).decode()

                done, result= users.add_user(DB, name, email, username, password)
                client_socket.send(result.encode())
                client_socket.send(done.encode())

                if done == "True": 
                    online_users[username] = client_socket
                    handle_client(client_socket, username)
                    break

            elif choice.upper() == 'L': 
                username = client_socket.recv(1024).decode()

                password = client_socket.recv(1024).decode()

                done, result = users.authenticate(DB, username, password)
                client_socket.send(result.encode())
                client_socket.send(done.encode())

                if done == "True": 
                    online_users[username] = client_socket
                    handle_client(client_socket, username)
                    break

            else:
                client_socket.send(msg.MESSAGES["INVALID_CHOICE"].encode())

    except Exception as e:
        print(f"Error handling client: {e}")

    finally: 
        client_socket.close()

def start(port): 
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', port))
    server.listen(5)
    print(f"Server listening on port {port}...")

    while True:
        client_socket, addr = server.accept()
        print(f"Connection established with {addr}")

        handler = threading.Thread(target=signOn_client, args=(client_socket,))
        handler.start()


if __name__ == '__main__':
    users.create(DB)
    Products.create(DB)

    port = int(input("Enter your port number: "))
    print(f"Listening on port {port}")

    start(port)
