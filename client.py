import socket
import os
import pathlib
import c_db
import ar_mess

def main():
    # Define server address and port
    server_address = '127.0.0.1'  # Replace with your server's IP address
    server_port = 12345           # Replace with your server's port

    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the server
        client_socket.connect((server_address, server_port))
        print(f"Connected to server at {server_address}:{server_port}")
        file_name =  "example.txt"  # Replace with the file you want to send

        # Send a message to the server
        message = {
            "name_of_file": file_name,
            "file_size": 1234,
            "update_date": 1633072800
        }
        client_socket.sendall(message.encode('utf-8'))
        print(f"Sent: {message}")

        # Receive a response from the server
        response = client_socket.recv(1024).decode('utf-8')
        print(f"Received: {response}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the connection
        client_socket.close()
        print("Connection closed.")






if __name__ == "__main__":
    directory()
    main()