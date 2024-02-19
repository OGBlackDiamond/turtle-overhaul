import socket
import threading

PORT = 8080
SERVER = socket.gethostbyname("rx-78-2")

ADD = (SERVER, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADD)


DISCONNECT_MESSAGE = "END-OF-LINE"

def handle_client(conn, add):
    print(f"NEW CONNECTION @ {add}")

    connected = True
    while connected:
        msg = conn.recv().decode("utf-8")

        if msg == DISCONNECT_MESSAGE:
            connected = False
        print(msg)

    conn.close()


def start():
    print("SERVER STARTING")
    server.listen()
    while True:
        conn, add = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, add))
        thread.start()
        print(f"ACTIVE CONNECTIONS: {threading.active_count() - 1}")

start()