import socket
import threading

# Server configuration
HOST = '0.0.0.0'  # Listen on all available interfaces
PORT = 12345      # Port to listen on

def handle_client(client_socket, client_address):
    print(f"New connection from {client_address}")
    client_socket.sendall(b"hello")  # Send "hello" to the client
    client_socket.close()            # Close the connection

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)  # Allow up to 5 queued connections
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        client_socket, client_address = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    start_server()