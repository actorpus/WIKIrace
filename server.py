import json
import random
import socket
import threading
import time
import os
import struct


# https://stackoverflow.com/questions/36500197/how-to-get-time-from-an-ntp-server
def RequestTimefromNtp(addr='0.de.pool.ntp.org'):
    REF_TIME_1970 = 2208988800  # Reference time
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = b'\x1b' + 47 * b'\0'
    client.sendto(data, (addr, 123))
    data, address = client.recvfrom(1024)
    if data:
        t = struct.unpack('!12I', data)[10]
        t -= REF_TIME_1970
    else:
        t = int(time.time())
    return t


class Client(threading.Thread):
    def __init__(self, sock):
        super().__init__()
        self.sock = sock
        self.name = "DEFAULT NAME"
        self.has_won = False
        self.running = True
        self.path = []
        self.daemon = True

    def start_message(self, start, end):
        self.sock.send(json.dumps({
            "start_point": start,
            "end_point": end,
            "start_time": RequestTimefromNtp() + 60
        }).encode())

    def broadcast_win(self, winning_path):
        self.sock.send(json.dumps({
            "gameover": 1,
            "path": winning_path
        }).encode())

    def run(self) -> None:
        data = self.sock.recv(1024)
        data = json.loads(data.decode())

        self.name = data["name"]
        print(self.name, "has registered and is waiting")

        time.sleep(1)

        self.sock.send(b'WELCOME')

        time.sleep(1)

        # wait for winning message
        while self.running:
            data = b""
            while not data:
                data = self.sock.recv(1024)

            if data == b'WIN':
                data = b""
                while not data:
                    data = self.sock.recv(16_384)

                self.path = json.loads(data.decode())

                self.has_won = True
                self.running = False
                continue

            print(data)


ip, port = socket.gethostbyname(socket.gethostname()), 37126
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.bind(("", port))
server_sock.listen(64)
print(f"server running on {ip}:{port}")


def run_server(players: int):
    clients = []

    for i in range(players):
        connection, client = server_sock.accept()

        print(f"{i + 1}/{players} new connection from", client)

        c = Client(connection)
        c.start()

        clients.append(c)

    print("all clients connected, building suspense...")
    time.sleep(10)

    with open("topviews-2022.json", "rb") as file:
        top_views = file.read()
        top_views = json.loads(top_views)

    start = random.choice(top_views)
    end = random.choice(top_views)

    print("starting with")
    print(start["article"])
    print("to")
    print(end["article"])

    for con in clients:
        con.start_message(start, end)

    print("waiting for winner to transmit")

    won = None
    while won is None:
        for con in clients:
            if con.has_won:
                won = con

    print("winner!", won.name, won.path)

    for con in clients:
        con.broadcast_win(won.path)
        con.running = False


while True:
    server_for = int(input("server for? \n> "))
    run_server(server_for)
