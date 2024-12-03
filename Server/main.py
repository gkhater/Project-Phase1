import socket
import threading
import os
import Users as users
import Products as Products
import Messages as msg
from Rates import convert

DB = 'auboutique.db'

online_users = {}

def get_users(): 
    return '\n\t'.join(online_users.keys())

def get_products(username): 
    currency = users.get_currency(DB, username)
    return '\n\t'.join([f"ID: {product[0]}, Name: {product[1]}, Count: {product[2]}, Description: {product[3]}, Price: {product[4] * convert('USD', currency)}, Seller: {product[5]}, Rating: {product[5]} ({product[6]} reviews)" 
                      for product in Products.fetch_products(DB)])

def is_online(username): 
    if username in online_users: 
        return msg.MESSAGES['USER_ONLINE'].format(username=username)
    return msg.MESSAGES['USER_OFFLINE'].format(username=username)

def handle_logout(client_socket, username):
    if username in online_users and online_users[username]["socket"] == client_socket: 
        del online_users[username]
    print(msg.MESSAGES['USER_DISCONNECTED'].format(username=username))
    client_socket.close()

def handle_text(client_socket, username, response):
    if len(response) > 1:
        destination= response[1]
        peer_address = get_peer_address(destination)
        if peer_address: 
            client_socket.send(f"PEER {peer_address[0]} {peer_address[1]} {username}".encode())
        else: 
            client_socket.send(f"{destination} is offline.".encode())
    else:
        client_socket.send("Invalid TEXT command. Use TEXT [username] [message].".encode())

def handle_help(client_socket):
    client_socket.send(msg.MESSAGES["HELP_PROMPT"].encode())

def handle_check(client_socket, response):
    if len(response) > 1:
        ans = is_online(response[1])
        client_socket.send(ans.encode())
    else:
        client_socket.send(msg.MESSAGES['INVALID_CHECK'].encode())

def handle_products(client_socket, username):
    products = "Available products: \n" + get_products(username)
    client_socket.send(products.encode())

def handle_buy(client_socket, username, response):
    if len(response) > 1:
        product_id = response[1].strip()
        result = Products.buy(DB, product_id, username)
        client_socket.send(result.encode())
    else:
        client_socket.send(msg.MESSAGES['INVALID_BUY'].encode())

def handle_add(client_socket, username, response):
    if len(response) > 3:
        count, name, price, description = response[1].strip(), response[2].strip(), response[3].strip(), " ".join(response[3:]).strip()
        result, ID = Products.add(DB, name, username, price, description, count=count)

        client_socket.send(result.encode())

        image_length = int(client_socket.recv(1024).decode())
        data = b""
        while len(data) < image_length:
            packet = client_socket.recv(1024)
            if not packet:
                break
            data += packet
        path = os.path.join("Images", f"ID_{ID}.png")
        try:
            with open(path, "wb") as img:
                img.write(data)
            client_socket.send(msg.MESSAGES['IMG_SUCCESS'].encode())
        except Exception as e:
            client_socket.send(msg.MESSAGES['IMG_ERROR'].encode())
    else:
        client_socket.send(msg.MESSAGES['INVALID_ADD'].encode())

def handle_sold(client_socket, username):
    result = Products.view_sold(DB, username)
    client_socket.send(result.encode())

def handle_online(client_socket):
    users_list = get_users()
    message = f"Online users: \n{users_list}"
    client_socket.send(message.encode())

def handle_rate(client_socket, response):
    if len(response) > 2:
        product_id, rating = response[1], int(response[2])
        if 1 <= rating <= 5:
            result = Products.rate_product(DB, product_id, rating)
            client_socket.send(result.encode())
        else:
            client_socket.send("Rating must be between 1 and 5.".encode())
    else:
        client_socket.send("Invalid RATE command. Use RATE [product_id] [rating].".encode())

def handle_search(client_socket, response):
    if len(response) > 1:
        query = " ".join(response[1:])
        results = Products.search_products(DB, query)
        if isinstance(results, list):
            message = "Search Results:\n" + "\n".join(
                [f"ID: {r[0]}, Name: {r[1]}, Price: {r[3]}, Seller: {r[4]}" for r in results]
            )
            client_socket.send(message.encode())
        else:
            client_socket.send(results.encode())
    else:
        client_socket.send("Invalid SEARCH command. Use SEARCH [query].".encode())

def handle_deposit(client_socket, username,response): 
    if len(response) > 1: 
        amount = response[1]
        answer = users.deposit(DB, username, int(amount))
    else: 
        answer = "Invalid syntax, Please use: DEPOSIT {amount}\n"
    
    client_socket.send(answer.encode())


def handle_balance(client_socket, username): 
    answer = str(users.get_balance(DB, username)) + '\n'
    client_socket.send(answer.encode())

def handle_currency(client_socket, username, response):
    if len(response) > 1: 
        answer = users.set_currency(DB, username, response[1])

    else: 
        answer = "Invalid syntax, Please use: CURRENCY {currency} \n available currencies: "
    
    client_socket.send(answer.encode())
def handle_unknown(client_socket):
    client_socket.send(msg.MESSAGES["UNKNOWN_COMMAND"].encode())

def handle_command(client_socket, username, response):
    command = response[0].upper()
    if command == "LOGOUT":
        return "LOGOUT"
    elif command == "TEXT":
        handle_text(client_socket, username, response)
    elif command == "HELPME":
        handle_help(client_socket)
    elif command == "CHECK":
        handle_check(client_socket, response)
    elif command == "PRODUCTS":
        handle_products(client_socket, username)
    elif command == "BUY":
        handle_buy(client_socket, username, response)
    elif command == "ADD":
        handle_add(client_socket, username, response)
    elif command == "SOLD":
        handle_sold(client_socket, username)
    elif command == "ONLINE":
        handle_online(client_socket)
    elif command == "RATE":
        handle_rate(client_socket, response)
    elif command == "SEARCH":
        handle_search(client_socket, response)
    elif command == "DEPOSIT": 
        handle_deposit(client_socket, username,response)
    elif command == "BALANCE": 
        handle_balance(client_socket, username)
    elif command == "CURRENCY": 
        handle_currency(client_socket, username, response)
    else:
        handle_unknown(client_socket)

def handle_client(client_socket, username):
    # Send initial prompt
    products = get_products(username)
    users_list = get_users()
    client_socket.send((msg.MESSAGES['PROMPT_USER'].format(items=products, users=users_list)).encode())

    try:
        while True:
            response = client_socket.recv(1024).decode().split(' ')
            if handle_command(client_socket, username, response) == "LOGOUT":
                break
    finally:
        handle_logout(client_socket, username)

def send_Message(username, destination, message): 
    if destination not in online_users: 
        return msg.MESSAGES["TEXT_OFFLINE"].format(destination=destination)
    
    destination_socket  = online_users[destination]
    message = f"[From {username}] {message}"
    destination_socket.send(message.encode())
    return msg.MESSAGES["TEXT_SUCCESS"].format(destination=destination)

def get_peer_address(username): 
    if username in online_users: 
        return online_users[username]["address"]
    return None

def signOn_client(client_socket, client_address): 
    try:
        while True: 
            choice = client_socket.recv(1024).decode()
            choice.strip()

            if choice.upper() == 'S': 
                name = client_socket.recv(1024).decode()

                email = client_socket.recv(1024).decode()

                username = client_socket.recv(1024).decode()

                password = client_socket.recv(1024).decode()

                p2p_port = client_socket.recv(1024).decode()

                done, result= users.add_user(DB, name, email, username, password)
                client_socket.send(result.encode())
                client_socket.send(done.encode())

                if done == "True": 
                    online_users[username] = {
                        "socket" : client_socket, 
                        "address": (client_address[0], p2p_port) #(IP, port)
                    }
                    handle_client(client_socket, username)
                    break
                
            elif choice.upper() == 'L': 
                username = client_socket.recv(1024).decode()

                password = client_socket.recv(1024).decode()

                p2p_port = client_socket.recv(1024).decode()

                done, result = users.authenticate(DB, username, password)
                client_socket.send(result.encode())
                client_socket.send(done.encode())

                if done == "True": 
                    online_users[username] = {
                        "socket" : client_socket, 
                        "address": (client_address[0], p2p_port) #(IP, port)
                    }
                    
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

        handler = threading.Thread(target=signOn_client, args=(client_socket, addr,))
        handler.start()

if __name__ == '__main__':
    users.create(DB)
    Products.create(DB)

    port = int(input("Enter your port number: "))
    print(f"Listening on port {port}")

    start(port)
