import json
import random
import socket
import threading
import time


class Client(threading.Thread):
    def __init__(self, sock):
        super().__init__()
        self.sock = sock
        self.name = "DEFAULT NAME"
        self.has_won = False
        self.running = True

    def start_message(self, start, end):
        self.sock.send(json.dumps({
            "start_point": start,
            "end_point": end
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
                self.has_won = True
                continue

            print(data)


server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.bind(("127.0.0.1", 37126))
server_sock.listen(8)


clients = []


for _ in range(1):
    connection, client = server_sock.accept()

    print("new connection from", client)

    c = Client(connection)
    c.start()

    clients.append(c)


time.sleep(10)

with open("topviews-2022.json", "rb") as file:
    top_views = file.read()
    top_views = json.loads(top_views)

start = random.choice(top_views)
end = random.choice(top_views)

print("starting with")
print(start)
print("to")
print(end)

for con in clients:
    con.start_message(start, end)

print("waiting for winner to transmit")

won = None
while won is None:
    for con in clients:
        if con.has_won:
            won = con

print("winner!", won.name)

for con in clients:
    con.running = False
