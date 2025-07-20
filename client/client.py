import os
import socket

# --- Server info
HOST = '0.0.0.0'
PORT = 1234
BUFFER_SIZE = 4096 #(4KB)

# --- Instructions
INSTRUCTIONS = '''
To download a file, simply enter: "DOWNLOAD [FILENAME]"
'''

# --- Functions
def download_image(file_size: int):
    new_image_name = input('How would you like to name the file?\n')

    bytes_received = 0
    with open(f'{new_image_name}.jpg', 'wb') as f:
        while bytes_received < file_size:
            bytes_read = client.recv(4096)
            if not bytes_read:
                break
            f.write(bytes_read)
            bytes_received += len(bytes_read)


def upload_image(image_name: str):
    img_size = str(os.path.getsize(image_name))
    client.send(f'{image_name} {img_size}'.encode())

    with open(image_name, 'rb') as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)

            if not bytes_read:
                break
            client.sendall(bytes_read)

# --- Client initialization
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))


# --- Main client logic
while True:
    print(client.recv(1024).decode())

    message = input()
    client.send(message.encode())

    server_message = client.recv(1024).decode().split()

    # Client request
    protocol = message.split()[0]
    file_name = message.split()[1]

    # Server response
    code = server_message[0]
    response = server_message[1]

    if code == 'OK':
        if protocol == 'DOWNLOAD':
            download_image(int(response))
        if protocol == 'UPLOAD':
            upload_image(file_name)
    else:
        print(f'{response}\n')