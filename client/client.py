import socket
import json
import struct
import base64

# --- Server info

HOST = '0.0.0.0'
PORT = 4444
HEADER_LENGTH = 4

# --- AUX Functions

def receive_all(sock: socket.socket, length: int) -> bytes | None:
    chunks = []
    bytes_recd = 0
    while bytes_recd < length:
        chunk = sock.recv(length - bytes_recd)

        if not chunk:
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

def download_image(FILE_SIZE: int):
    IMG_NAME_LOCAL = input('\nHow would you like to name the file?\n')

    bytes_recieved = 0
    with open(f'{IMG_NAME_LOCAL}.jpg', 'wb') as f:
        while bytes_recieved < FILE_SIZE:

            server_payload = receive_message(client)

            base64_data = server_payload['data'].encode()
            bytes_read = base64.b64decode(base64_data)
            
            if not bytes_read:
                break
            f.write(bytes_read)
            bytes_recieved += len(bytes_read)


# --- Client initialization

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))


# --- Main client logic

while True:
    client_input = input().split()
    command = client_input[0]

    if command == 'DOWNLOAD' or command == 'UPLOAD':
        client.send(assemble_message({'command': command,
                                      'filename': client_input[1]}))
    else:
        client.send(assemble_message({'command': command}))

    server_response = receive_message(client)

    match server_response['status']:
        case 'SENDING_AVAILABLE_FILES':
            file_list = receive_message(client)['data']
            print(file_list)
        
        case 'STARTING_TRANSFER':
            download_image(server_response['filesize'])
        
        case _:
            print(server_response['details'])