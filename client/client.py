import socket

# --- Server info
HOST = '0.0.0.0'
PORT = 9999

# --- Functions
def download_image():
    IMG_NAME_LOCAL = input('How would you like to name the file?\n')

    IMG_SIZE_STR = client.recv(64).decode('utf-8')
    IMG_SIZE = int(IMG_SIZE_STR)

    bytes_recieved = 0
    with open(f'{IMG_NAME_LOCAL}.jpg', 'wb') as f:
        while bytes_recieved < IMG_SIZE:
            bytes_read = client.recv(4096)
            if not bytes_read:
                break
            f.write(bytes_read)
            bytes_recieved += len(bytes_read)


# --- Client initialization
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))


# --- Main client logic
print(client.recv(1024).decode())
while True:
    message = input()
    client.send(message.encode())
    server_message = client.recv(1024).decode()

    if server_message == 'SENDING_IMAGE':
        download_image()
        print(client.recv(1024).decode())
    else:
        print(server_message)