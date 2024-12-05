import socket
import threading

# Function to handle receiving messages from the server
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message:
                print(f"\n[Server]: {message}\n> ", end="")
            else:
                break  # Connection closed by the server
        except Exception as e:
            print(f"\nError receiving message: {e}")
            break

def main():
    server_address = 'localhost'  # Server hostname or IP
    server_port = 5001           # Server port

    # Create and connect the client socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_address, server_port))
    print(f"Connected to server at {server_address}:{server_port}")

    # Start a thread to listen for incoming messages
    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

    try:
        while True:
            user_input = input("> ").strip()
            if user_input.lower() == "exit":
                print("Disconnecting...")
                break
            client_socket.send(user_input.encode())  # Send message to the server
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        print("Connection closed.")

if __name__ == "__main__":
    main()
