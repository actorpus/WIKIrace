import hashlib
import json
import random
import socket
import threading
import time
import os
import struct


def xor_bytes(bytes_1, bytes_2):
    if len(bytes_2) < len(bytes_1):
        bytes_1, bytes_2 = bytes_2, bytes_1

    return bytes(a ^ b for a, b in zip(bytes_1, bytes_2))


def salt_and_hash(password, salt):
    password = hashlib.sha256(password.encode()).digest()
    password = xor_bytes(password, salt)
    password = hashlib.sha256(password).digest()
    return password


class Client(threading.Thread):
    def __init__(self, sock, has_password=False, password=""):
        super(Client, self).__init__()
        self.daemon = True

        self._sock: socket.SocketType = sock
        self._server_has_password = has_password
        self._server_password = password

        self.name = f"CLIENT{random.randbytes(5).hex()}"
        self.has_won = False
        self.alive = True
        self._last_heartbeat = time.time()
        self._salt = random.randbytes(32)
        self._authorised = False
        self.is_waiting = False

        # stuff for when the client has won
        self.path = []

    @property
    def _locale_password(self):
        return salt_and_hash(
            self._server_password,
            self._salt
        )

    def _recv(self, data):
        if data == b"":
            return

        if data == b"JOIN":
            print(f" [ \033[0;35mC\033[0;0m ] Join packet from {self.name}")

            self._sock.send(b"CNTU")

            if self._server_has_password:
                self._sock.send(b"\x01")
                self._sock.send(self._salt)
                return

            self._sock.send(b"\x00")
            return

        if data == b"NAME":
            name = self._sock.recv(16).decode()
            print(f" [ \033[0;35mC\033[0;0m ] Client ({self.name}) changed there name to ", end="")
            self.name = name.replace("_", "")
            print(f"({self.name})")
            return

        if data == b"PSWD":
            password = self._sock.recv(32)

            if password == self._locale_password:
                self._authorised = True
                print(f" [ \033[0;35mC\033[0;0m ] Client ({self.name}) successfully authorised")

            return

        if data == b"REDY":
            if self._server_has_password and not self._authorised:
                print(f" \033[0;31m[ \033[0;35mC\033[0;0m \033[0;31m]\033[0;0m Client ({self.name}) tried to join the game with inadequate authorisation")
                self.alive = False
                self._sock.send(b"PISS")
                self._sock.close()
                return

            self.is_waiting = True
            self._sock.send(b"WAIT")
            print(f" [ \033[0;35mC\033[0;0m ] Client ({self.name}) is now waiting")
            return

        if data == b"HART":
            self._last_heartbeat = time.time()
            self._sock.send(b"HART")
            return

        if data == b"TMPK":
            t = time.time()
            t = int(t * 2 ** 16).to_bytes(6, 'big')

            self._sock.send(b"TMPK")
            self._sock.send(t)

            return

        print(f" [ \033[0;35mC\033[0;0m ] Client ({self.name}) sent a bad packet, {data=}")

    def run(self) -> None:
        while self.alive:
            # only attempt to recv for 1 seconds
            self._sock.settimeout(1)

            try:
                self._recv(self._sock.recv(4))
                # this call could close the socket, no socket calls until while loop ends.

            except socket.timeout:
                ...

            except ConnectionResetError:
                print(f" \033[0;31m[ \033[0;35mC\033[0;0m \033[0;31m]\033[0;0m Client ({self.name}) has closed there socket, assuming the worst")
                self.alive = False

    def rebind(self, _):
        raise NotImplementedError

    def broadcast_start(self, start, end):
        self._sock.send(b"STRT")


ip, port = socket.gethostbyname(socket.gethostname()), 16124
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.bind(("", port))
server_sock.listen(64)
print(f"server running on {ip}:{port}")


def run_server(players: int):
    clients = {}

    waiting = True
    while waiting:
        if len(clients) < players:
            server_sock.settimeout(1)

            try:
                connection, client = server_sock.accept()
            except socket.timeout:
                continue
            else:
                server_sock.settimeout(None)

                print(f" [ \033[0;36mS\033[0;0m ] New connection from {client[0]}:{client[1]} {len(clients) + 1}/{players}")

                if client in clients:
                    clients[client].rebind(connection)
                    continue

                c = Client(connection, has_password=True, password="password")
                clients[client] = c
                c.start()

                # allow time for client to properly start up, potential for premature abandonment
                time.sleep(1)

        if all(clients[client].is_waiting for client in clients):
            waiting = False

        else:
            for bad_client in [client for client in clients if not clients[client].alive]:
                print(f" [ \033[0;36mS\033[0;0m ] Abandoning {bad_client[0]}:{bad_client[1]}")
                del clients[bad_client]
                print(f" [ \033[0;36mS\033[0;0m ] Waiting for connection...  {len(clients)}/{players}")

    print(f" [ \033[0;36mS\033[0;0m ] All clients now authorised, starting game")
    print(f" [ \033[0;36mS\033[0;0m ] Picking starting and ending points")

    with open("topviews-2022.json", "rb") as file:
        top_views = file.read()
        top_views = json.loads(top_views)

    start = random.choice(top_views)
    end = random.choice(top_views)

    print("     ├ START: ", start["article"])
    print("     └ END:   ", end["article"])

    time.sleep(10)

    for client in clients:
        clients[client].broadcast_start(start["article"], end["article"])

server_for = int(input("server for? \n> "))
run_server(server_for)

input()
