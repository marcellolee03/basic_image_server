import socket

# --- Server info
HOST = '0.0.0.0'
PORT = 1234

# --- Instructions
INSTRUCTIONS = '''
To download a file, simply enter: "DOWNLOAD [FILENAME]"
'''

# --- Functions
def download_image(FILE_SIZE: int):
    IMG_NAME_LOCAL = input('How would you like to name the file?\n')

    bytes_recieved = 0
    with open(f'{IMG_NAME_LOCAL}.jpg', 'wb') as f:
        while bytes_recieved < FILE_SIZE:
            bytes_read = client.recv(4096)
            if not bytes_read:
                break
            f.write(bytes_read)
            bytes_recieved += len(bytes_read)


# --- Client initialization
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))


# --- Main client logic
while True:
    print(client.recv(1024).decode())

    message = input()
    client.send(message.encode())

    server_message = client.recv(1024).decode().split()

    code = server_message[0]
    response = server_message[1]

    if code == 'OK':
        download_image(int(response))
    else:
        print(f'{response}\n')