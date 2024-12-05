import socket
import threading
import os
import Users as users
import Products as Products
import Messages as msg
import json 
import base64
from Rates import convert


DB = 'auboutique.db'

online_users = {}

def get_users(): 
    return list(online_users.keys())

def get_products(username): 
    currency = users.get_currency(DB, username)
    data = { 
        product[0]: {
        "Name": product[1],
        "Count": product[2],
        "Description": product[3],
        "Price": product[4] * convert("USD", currency),
        "Seller": product[5],
        "Rating": product[6],
        "Reviews": product[7],
        # "Image": get_image(2)
    }
    for product in Products.fetch_products(DB)
    }

    return data

def get_image(ID): 
    img_path = f"Images\ID_{ID}.jpg"
    with open(img_path, 'rb') as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')  # Decode to convert bytes to a string

    encoded_image = json.dumps(encoded_image)
    print(encoded_image)
    return encoded_image


def is_online(username): 
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    if username in online_users: 
        data = { 
            "code": 200, 
            "online": True
        }
        
    else: 
        data = { 
            "code": 200, 
            "online": False
        }
    
    return data

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
            data = {
                "code" : 200, 
                "IP_address" : peer_address[0], 
                "port": peer_address[1], 
                "username": username
            }

        else: 
            data = {
                "code" : 404, 
                "error": f"Username {username} is offline"
            }
    else:
        data = { 
            "code": 400, 
            "error": "Invalid TEXT command."
        }
    
    print(data)
    json_data = json.dumps(data, indent=4)
    client_socket.sendall(json_data.encode('utf-8'))

#TODO implement with json
def handle_help(client_socket):
    client_socket.send(msg.MESSAGES["HELP_PROMPT"].encode())

def handle_check(client_socket, response):
    if len(response) > 1:
        data = is_online(response[1])
        json_data = json.dumps(data, indent=4)
        client_socket.sendall(json_data.encode('utf-8'))
    else:
        data = {
            "code": 400, 
            "error": "Invalid command."
        }

        print(data)
        json_data = json.dumps(data, indent=4)
        client_socket.sendall(json_data.encode('utf-8'))

def handle_products(client_socket, username):
    data = get_products(username)

    json_data = json.dumps(data, indent=4)
    client_socket.sendall(json_data.encode('utf-8'))

def handle_buy(client_socket, username, response):
    if len(response) > 1:
        product_id = response[1].strip()
        result = Products.buy(DB, product_id, username)
        client_socket.sendall(result.encode('utf-8'))
    else:
        data = {
            "code": 400, 
            "error": "Invalid BUY"
        }

        print(data)
        json_data = json.dumps(data, indent=4)
        client_socket.sendall(json_data.encode('utf-8'))

def handle_add(client_socket, username, response):
    if len(response) > 3:
        count, name, price, description = response[1].strip(), response[2].strip(), response[3].strip(), " ".join(response[4:]).strip()
        print(f"{name}, {username}, {price}, {description}, {count}")
        data, ID = Products.add(DB, name, username, price, description, count=count)

        # image_length = int(client_socket.recv(1024).decode())
        # data = b""
        # while len(data) < image_length:
        #     packet = client_socket.recv(1024)
        #     if not packet:
        #         break
        #     data += packet
        # path = os.path.join("Images", f"ID_{ID}.png")
    else:
        data = { 
            "code": 400, 
            "error": "Invalid add."
        }

    print(data)

    json_data = json.dumps(data, indent=4)
    client_socket.sendall(json_data.encode('utf-8'))

def handle_sold(client_socket, username):
    result = Products.view_sold(DB, username, username)
    client_socket.sendall(result.encode('utf-8'))

def handle_online(client_socket):
    users_list = get_users()
    data = { 
        "code": 200, 
        "users": users_list
    }

    print(data)
    json_data = json.dumps(data, indent=4)
    client_socket.sendall(json_data.encode('utf-8'))

def handle_rate(client_socket, response):
    if len(response) > 2:
        product_id, rating = response[1], int(response[2])
        if 1 <= rating <= 5:
            data = Products.rate_product(DB, product_id, rating)
            
        else:
            data = {
                "code": 400, 
                "error": "Rating must be between 1 and 5."
            }
    else:
        data = { 
            "code": 400, 
            "error": "Invalid command."
        }
    
    print(data)
    json_data = json.dumps(data, indent=4)
    client_socket.sendall(json_data.encode('utf-8'))

def handle_search(client_socket, response):
    if len(response) > 1:
        query = " ".join(response[1:])
        results = Products.search_products(DB, query)
        if isinstance(results, list):

            data  = {
                "Search Results": {
                    r[0]: {
                        "Name": r[1],
                        "Price": r[3],
                        "Seller": r[4]
                    }
                    for r in results
                }
            }
        else:
            data = {
                "code": 500, 
                "error": "Internal error searching product"
            }
    else:
        data = {
            "code": 400, 
            "error": "Invalid search command."
        }

    print(data)
    json_data = json.dumps(data, indent=4)
    client_socket.sendall(json_data.encode('utf-8'))

def handle_deposit(client_socket, username,response): 
    if len(response) > 1: 
        amount = response[1]
        data = users.deposit(DB, username, int(amount))
    else: 
        data = {
            "code": 400, 
            "error": "Invalid Request."
        }
    
    print(data)
    json_data = json.dumps(data, indent=4)
    client_socket.sendall(json_data.encode('utf-8'))


def handle_balance(client_socket, username): 
    data = users.get_balance(DB, username)

    print(data)
    json_data = json.dumps(data, indent=4)
    client_socket.sendall(json_data.encode('utf-8'))

def handle_currency(client_socket, username, response):
    if len(response) > 1: 
        data = users.set_currency(DB, username, response[1])

    else: 
        data = { 
            "code" : 400, 
            "error": "Invalid Request."
        }

    print(data)
    json_data = json.dumps(data, indent=4)
    client_socket.sendall(json_data.encode('utf-8'))
    
def handle_unknown(client_socket):
    data = { 
        "code": 400, 
        "error": "Unknown command."
    }

    print(data)
    json_data = json.dumps(data, indent=4)
    client_socket.sendall(json_data.encode('utf-8'))

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

def handle_client(client_socket, username, name):
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
            #TODO serialize
            choice = client_socket.recv(1024).decode()
            choice.strip()

            if choice.upper() == 'S': 
                name = client_socket.recv(1024).decode()

                email = client_socket.recv(1024).decode()

                username = client_socket.recv(1024).decode()

                password = client_socket.recv(1024).decode()


                done, result= users.add_user(DB, name, email, username, password)
                client_socket.send(result.encode())
                client_socket.send(done.encode())

                break
                
            elif choice.upper() == 'L': 
                print("hi baba")
                username = client_socket.recv(1024).decode()

                print(username)
                password = client_socket.recv(1024).decode()

                print(password)
                p2p_port = client_socket.recv(1024).decode()

                print("AAAAAAAAAAAAAAAA")
                done, realname = users.authenticate(DB, username, password)

                print("DONE: " + done)
                code = 400
                if done == "True": 
                    code = 200
                
                
     
                data = {
                    "code" : code, 
                    "name": realname, 
                }

                print(data)

                json_data = json.dumps(data, indent=4)

                client_socket.sendall(json_data.encode('utf-8'))

                if code == 200: 
                    online_users[username] = {
                        "socket" : client_socket, 
                        "address": (client_address[0], p2p_port) #(IP, port)
                    }

                    print(f"code: {code}")
                    
                    handle_client(client_socket, username, realname)
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