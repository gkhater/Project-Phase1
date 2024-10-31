import socket
import threading
import os 
import time

#Thread to handle incoming messages asynchronously.
def receive_messages(client_socket):
    while True:
        try:
            server_message = client_socket.recv(1024).decode()
            if server_message:
                print(f"\n[Server]: {server_message} \n>", end = "")  
            else:
                print("\nConnection closed by server.")
                break
        except Exception as e:
            print(f"\nError receiving message: {e}")
            break

def register(client_socket):
    try:
        name = input("Enter your name: ").strip()
        client_socket.send(name.encode())  

        email = input("Enter your email: ").strip()
        client_socket.send(email.encode())  

        username = input("Enter your username: ").strip()
        client_socket.send(username.encode())  

        password = input("Enter your password: ").strip()
        client_socket.send(password.encode())  

        server_message = client_socket.recv(1024).decode()
        print(server_message)
        done = client_socket.recv(1024).decode()

        return done

    except Exception as e:
        print(f"Error during registration: {e}")
        return "False"

def log_in(client_socket): 
    try:
        username = input("Enter your username: ").strip()
        client_socket.send(username.encode())  

        password = input("Enter your password: ").strip()
        client_socket.send(password.encode())  

        server_message = client_socket.recv(1024).decode()
        print(server_message)
        done = client_socket.recv(1024).decode()
        
        return done

    except Exception as e:
        print(f"Error during login: {e}")
        return None

def add_product(client_socket): 
    time.sleep(0.5)
    
    image_path = input("Enter the full path to the image file: ")
    if not os.path.isfile(image_path): 
        print("Invalid Image path, will use default image")
        client_socket.send(f"0".encode())
        client_socket.send(f"No img data".encode())
        return 
    
    try: 
        with open(image_path, "rb") as img: 
            data = img.read()
        
        client_socket.send(f"{len(data)}".encode())
        client_socket.sendall(data)
    except Exception as e: 
        print(f"Error sending image {e}")
        client_socket.send(f"0".encode())
        client_socket.send(f"No img data".encode())
        
def talk_to_server(client_socket): 
    while True: 
        threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()
        user_input = input().strip().upper()

        client_socket.send(user_input.encode())

        user_split = user_input.split(' ')
        if(user_split[0] == 'ADD' and len(user_split) > 3): 
            add_product(client_socket)

        if user_input.upper() == "LOGOUT": 
            print("Logging out...")
            break         

def signOn(domain_name, port): 
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Start the thread for receiving messages
    try:
        client_socket.connect((domain_name, port))
        print(f"Connected to server at {domain_name}:{port}")

        while True:

            user_input = input("Welcome to AUBoutique! Do you want to: \n\t[S] Sign up\n\t[L] Log in\n>").strip()

            client_socket.send(user_input.encode())
            done = "False"
            
            if user_input.upper() == 'S':
                done = register(client_socket)
            elif user_input.upper() == 'L': 
                done = log_in(client_socket)
            else: 
                server_message = client_socket.recv(1024).decode()
                print(server_message)

            if done == "True": 
                talk_to_server(client_socket)
                break
            if user_input.upper() == 'LOGOUT': 
                break

    except Exception as e:
        print(f"Error: {e}")

    finally:
        print("Closing connection.")
        client_socket.close()

if __name__ == "__main__":
    domain_name = 'localhost'
    port = 5001
    signOn(domain_name, port)
