import socket
import sys

HOST, PORT = "localhost", 9999
data = " ".join(sys.argv[1:])

# Create a socket (SOCK_STREAM means a TCP socket)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    # Connect to server and send data
    sock.connect((HOST, PORT))

    while True:
        user_input = input("Type: ")
        sock.sendall(bytes(user_input, "utf-8"))

        # Receive data from the server and shut down
        received = str(sock.recv(1024), "utf-8")