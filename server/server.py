import socket
import threading
import os

# --- Server Configurations
HOST = '0.0.0.0'
PORT = 1234
MAX_CLIENTS = 5
BUFFER_SIZE = 4096 #(4KB)

# --- Functions
def accept_client():
    while True:
        client, addr = server.accept()
        print(f'Client {client} has just connected.')

        handle_client(client)


def handle_client(client):
    while True:
        show_available_images(client)

        client_response = client.recv(1024).decode().split()

        try:
            protocol = client_response[0]
            file_name = client_response[1]
            
            if protocol == 'DOWNLOAD':
                if os.path.exists(file_name):
                    send_image(client, file_name)
                else:
                    client.send('ERROR FILE_NOT_FOUND'.encode())

            if protocol == 'UPLOAD':
                receive_image(client)
            else:
                client.send('ERROR INVALID_COMMAND'.encode())

        except IndexError:
            client.send('ERROR BAD_ARGUMENT'.encode())


def show_available_images(client):

    # Printing all available images
    image_listing = 'AVAILABLE IMAGES: \n'

    for root, _, files in os.walk(os.getcwd()):
        for file in files:
            if file.lower().endswith('.jpg'):
                image_listing += f'{file}\n'
    
    client.send(image_listing.encode())


def send_image(client, img_name: str):

    img_size = str(os.path.getsize(img_name))
    client.send(f'OK {img_size}'.encode())

    with open(img_name, 'rb') as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)

            if not bytes_read:
                break
            client.sendall(bytes_read)


def receive_image(client):
    client.send('OK AWAITING_FILE_DATA'.encode())

    # Receiving file data
    file_data = client.recv(1024).decode().split()
    file_name = file_data[0]
    file_size = file_data[1]

    bytes_received = 0
    with open(f'{file_name}.jpg', 'wb') as f:
        while bytes_received < file_size:
            bytes_read = client.recv(4096)
            if not bytes_read:
                break
            f.write(bytes_read)
            bytes_received += len(bytes_read)

# --- Server Initialization
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen(MAX_CLIENTS)

    accept_thread = threading.Thread(target = accept_client)
    accept_thread.start()