import socket
import threading
import os

# Thread to handle incoming P2P messages
def listen_for_p2p(p2p_socket):
    def handle_peer_connection(conn, addr):
        try:
            peer_message = conn.recv(1024).decode()
            print(f"\n[Peer {addr[0]}:{addr[1]}]: {peer_message}\n>", end="")
        except Exception as e:
            print(f"Error handling P2P message from {addr}: {e}")
        finally:
            conn.close()

    while True:
        try:
            conn, addr = p2p_socket.accept()  # Accept P2P connection
            threading.Thread(target=handle_peer_connection, args=(conn, addr), daemon=True).start()
        except Exception as e:
            print(f"Error in P2P listener: {e}")
            break

def receive_messages(client_socket):
    while True:
        try:
            server_message = client_socket.recv(1024).decode()
            if server_message:
                print(f"\n[Server]: {server_message} \n>", end = "")  
            else:
                break
        except Exception as e:
            print(f"\nError receiving message: {e}")
            break

# Register a new user
def register(tcp_socket, p2p_port):
    try:
        name = input("Enter your name: ").strip()
        tcp_socket.send(name.encode())

        email = input("Enter your email: ").strip()
        tcp_socket.send(email.encode())

        username = input("Enter your username: ").strip()
        tcp_socket.send(username.encode())

        password = input("Enter your password: ").strip()
        tcp_socket.send(password.encode())

        tcp_socket.send(str(p2p_port).encode())  # Send P2P port to the server

        server_message = tcp_socket.recv(1024).decode()
        print(server_message)
        done = tcp_socket.recv(1024).decode()

        return done
    except Exception as e:
        print(f"Error during registration: {e}")
        return "False"

# Log in an existing user
def log_in(tcp_socket, p2p_port):
    try:
        username = input("Enter your username: ").strip()
        tcp_socket.send(username.encode())

        password = input("Enter your password: ").strip()
        tcp_socket.send(password.encode())

        tcp_socket.send(str(p2p_port).encode())  # Send P2P port to the server

        server_message = tcp_socket.recv(1024).decode()
        print(server_message)
        done = tcp_socket.recv(1024).decode()

        return done
    except Exception as e:
        print(f"Error during login: {e}")
        return None

# Send a P2P message to a peer
def send_p2p(ip, port, message):
    try:
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.connect((ip, int(port)))
        peer_socket.send(message.encode())
        peer_socket.close()
        print(f"Message sent to {ip}:{port}")
    except Exception as e:
        print(f"Error sending P2P message to {ip}:{port}: {e}")

# Handle the TEXT command to send P2P messages
def handle_text(tcp_socket, user_split):
    if len(user_split) <= 2:
        print("Invalid syntax. Use TEXT {username} {message}")
    else:
        target_user = user_split[1]
        message = " ".join(user_split[2:])

        # Request peer info from the server
        tcp_socket.send(f"TEXT {target_user}".encode())
        response = tcp_socket.recv(1024).decode()

        if response.startswith("PEER"):
            _, ip, port, username  = response.split(" ")
            message = f"[{username}] {message}"
            send_p2p(ip, int(port), message)
        else:
            print(response)  # Handle offline or invalid user cases

# Main server interaction loop
def talk_to_server(tcp_socket, p2p_port):
    messages = threading.Thread(target=receive_messages, args=(tcp_socket,), daemon=True)
    messages.start()

    start_p2p_listener(p2p_port)
    while True:
        user_input = input().strip()
        tcp_socket.send(user_input.encode())

        user_split = user_input.split(' ')
        if user_split[0].upper() == 'TEXT':
            handle_text(tcp_socket, user_split)

        elif user_input.upper() == "LOGOUT":
            print("Logging out...")
            messages.join()
            break

# Start the P2P listener
def start_p2p_listener(p2p_port):
    p2p_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    p2p_socket.bind(("", p2p_port))  # Bind to all available network interfaces
    p2p_socket.listen(5)
    threading.Thread(target=listen_for_p2p, args=(p2p_socket,), daemon=True).start()
    return p2p_socket

# Entry point for the client
def signOn(domain_name, tcp_port, p2p_port):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((domain_name, tcp_port))
    print(f"Connected to server at {domain_name}:{tcp_port}")

    try:
        while True:
            user_input = input("Welcome to AUBoutique! Do you want to: \n\t[S] Sign up\n\t[L] Log in\n>").strip()
            tcp_socket.send(user_input.encode())

            done = None
            if user_input.upper() == 'S':
                done = register(tcp_socket, p2p_port)
            elif user_input.upper() == 'L':
                done = log_in(tcp_socket, p2p_port)
            else:
                server_message = tcp_socket.recv(1024).decode()
                print(server_message)

            if "True" in done:
                talk_to_server(tcp_socket, p2p_port)
                break
            if user_input.upper() == 'LOGOUT':
                break

    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Closing connection.")
        tcp_socket.close()

if __name__ == "__main__":
    domain_name = 'localhost'
    tcp_port = 5001  # Server port
    p2p_port = 7001 # P2P listener port
    signOn(domain_name, tcp_port, p2p_port)
