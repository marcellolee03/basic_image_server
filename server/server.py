import socket
import threading
import os
import struct
import json
import base64

# --- Server Configurations
HOST = '0.0.0.0'
PORT = 4444
MAX_CLIENTS = 5
HEADER_LENGTH = 4
BUFFER_SIZE = 4096 #(4KB)

# --- AUX Functions
def receive_all(sock: socket.socket, length: int) -> bytes | None:
    chunks = []
    bytes_recd = 0
    while bytes_recd < length:
        chunk = sock.recv(length - bytes_recd)

        if not chunk:
            # Connection was closed by user
            return None
        
        chunks.append(chunk)
        bytes_recd += len(chunk)

    return b''.join(chunks)


def receive_message(client_socket: socket.socket) -> dict | None:
    try:
        header_bytes = receive_all(client_socket, HEADER_LENGTH)
        if not header_bytes:
            print(f'{client_socket} disconnected. Could not read header')

        message_length = struct.unpack('!I', header_bytes)[0]

        message_bytes = receive_all(client_socket, message_length)
        if not message_bytes:
            print(f'{client_socket} disconnected. Could not get payload')
        
        message = message_bytes.decode()
        return json.loads(message)

    except(struct.error, json.JSONDecodeError) as e:
        print(f'Error while processing message: {e}')
        return None
    
    except Exception as e:
        print(f'Unexpected error: {e}')
        return None


def assemble_message(payload_dict) -> bytes:
    payload = json.dumps(payload_dict)
    header = struct.pack('!I', len(payload))
    return header + payload.encode()

# --- Functions
def accept_client():
    while True:
        client, addr = server.accept()
        print(f'Client {addr} has just connected.')

        handle_client_thread = threading.Thread(target=handle_client, args=(client,))
        handle_client_thread.start()


def handle_client(client: socket.socket):
    while True:
        payload = receive_message(client)

        if not payload:
            break

        match payload['command']:
            case 'LIST_FILES':
                show_available_images(client)
            case 'DOWNLOAD':
                filename = payload['filename']
                send_image(client, filename)
            case _:
                payload_dict = {'status': 'ERROR',
                                'details': 'INVALID COMMAND'}
                client.send(assemble_message(payload_dict))


def show_available_images(client):

    payload_dict = {'status': 'SENDING_AVAILABLE_FILES'}
    client.send(assemble_message(payload_dict))

    # Printing all available images
    image_listing = 'AVAILABLE FILES: \n'

    for root, _, files in os.walk(os.getcwd()):
        for file in files:
            if file.lower().endswith('.jpg'):
                image_listing += f'{file}\n'
    
    image_listing = image_listing[:-1]

    payload_dict = {"type": "FILE_LIST",
                    "data": image_listing}

    client.send(assemble_message(payload_dict))


def send_image(client, filename):
    filesize = str(os.path.getsize(filename))

    # Changing client state to RECEIVING_FILE
    payload_dict = {"status": "STARTING_TRANSFER",
                    "filesize": int(filesize)}
    client.send(assemble_message(payload_dict))

    with open(filename, 'rb') as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)

            if not bytes_read:
                break

            encoded_chunk = base64.b64encode(bytes_read).decode()
            payload_dict = {"type": "FILE_CHUNK",
                            "data": encoded_chunk}

            client.send(assemble_message(payload_dict))
    


# --- Server Initialization
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(MAX_CLIENTS)

accept_thread = threading.Thread(target = accept_client)
accept_thread.start()