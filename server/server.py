import socket
import threading
import os

# --- Server Configurations
HOST = '0.0.0.0'
PORT = 9999
MAX_CLIENTS = 5
BUFFER_SIZE = 4096 #(4KB)

# --- Functions
def accept_client():
    while True:
        client, addr = server.accept()
        print(f'Client {client} just connected.')

        handle_client(client)


def handle_client(client):
    while True:
        operation_menu_str = \
        '--- Choose operation\n' \
        '-- 0 (DOWNLOAD Image)\n' \
        '-- 1 (UPLOAD Image)\n'

        client.send(operation_menu_str.encode())

        try:
            operation = int(client.recv(1024).decode())
            if (operation == 0):
                show_available_images(client)

        except ValueError:
            client.send('Invalid operation.'.encode())


def show_available_images(client):
    while True:
        images = {}
        i = 0

        # Printing all available images
        for root, _, files in os.walk(os.getcwd()):
            for file in files:
                if file.lower().endswith('.jpg'):
                    images.update({i: file})
                    i+=1
        
        image_listing = 'AVAILABLE IMAGES: \n'
        for i, img in images.items():
            image_listing += f'{i} -- {img}\n'
        
        client.send(image_listing.encode())
        
        print(images)
        # Sending chosen image to client
        try:
            choice = int(client.recv(1024).decode())
            send_image(client, images[choice])
            break
        except ValueError:
            client.send('Invalid answer.'.encode())
        except KeyError:
            client.send('Invalid answer'.encode())



def send_image(client, IMG_NAME: str):
    client.send('SENDING_IMAGE'.encode())

    IMG_SIZE_str = str(os.path.getsize(IMG_NAME))
    IMG_SIZE_bytes = IMG_SIZE_str.encode('utf-8')
    
    header = IMG_SIZE_bytes + b' ' * (64 - len(IMG_SIZE_bytes))
    client.send(header)

    with open(IMG_NAME, 'rb') as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)

            if not bytes_read:
                break
            client.sendall(bytes_read)


# --- Server Initialization
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen(MAX_CLIENTS)

    accept_thread = threading.Thread(target = accept_client)
    accept_thread.start()