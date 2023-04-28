__author__ = "actorp.us#7755"
__version__ = "1.16"
__licence__ = "CC BY-NC-SA 4.0"

#
# This work is licenced under Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International
#
# This license requires that reusers give credit to the creator. It allows reusers to distribute, remix,
# adapt, and build upon the material in any medium or format, for noncommercial purposes only. If others
# modify or adapt the material, they must license the modified material under identical terms.
# see more at https://creativecommons.org/licenses/by-nc-sa/4.0/
#
# official page for this project is https://github.com/actorpus/WIKIRace
#


import threading
import hashlib
import time
import json
import socket
import sys
import os
import struct

# enable debug mode if you plan on changing anything but want default settings
# enable dumb dumb mode if your running at school

DEBUG_MODE = True
DUMB_DUMB_MODE = False
UPDATE_SERVER = "https://raw.githubusercontent.com/actorpus/WIKIrace/main/"
LOCAL_PATH = sys.path[0].replace("\\", "/")
REF_TIME_1970 = 2208988800

SCHOOL_BYPASS_CACERT = """
Sophos SSL CA_C4005CM7MF2DV28
==================
-----BEGIN CERTIFICATE-----
MIIEiTCCA3GgAwIBAgIBATANBgkqhkiG9w0BAQsFADCBjTELMAkGA1UEBhMCR0Ix
FDASBgNVBAgMC094Zm9yZHNoaXJlMQ8wDQYDVQQKDAZTb3Bob3MxDDAKBgNVBAsM
A05TRzEmMCQGA1UEAwwdU29waG9zIFNTTCBDQV9DNDAwNUNNN01GMkRWMjgxITAf
BgkqhkiG9w0BCQEWEnN1cHBvcnRAc29waG9zLmNvbTAiGA8yMDE1MDgwMTAwMDAw
MFoYDzIwMzYxMjMxMjM1OTU5WjCBjTELMAkGA1UEBhMCR0IxFDASBgNVBAgMC094
Zm9yZHNoaXJlMQ8wDQYDVQQKDAZTb3Bob3MxDDAKBgNVBAsMA05TRzEmMCQGA1UE
AwwdU29waG9zIFNTTCBDQV9DNDAwNUNNN01GMkRWMjgxITAfBgkqhkiG9w0BCQEW
EnN1cHBvcnRAc29waG9zLmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoC
ggEBAN4RC0T/0We7xleGXWWFcNy/d3WVK/qloa2q4KAq25D6WTa8w/plSoL4L3+d
BIq71LbwKxWHVWxY3WmZBjbc7iLyRfwNJTRfSuf16j+T+13qJejIsn351BEFi+es
c79DN0ZPtZhQ5d+wHWRec8qj1+accTEHynV07A0v9gp2yoUPFdAX1BqQSfG37djD
bGgfj7TQO7+31RN8m6c8D8nQ8pRbxGkDmTvtNxxwOLLkUrPwCjGs2IvR8n3NKIkB
HemuWwSwpO9DbeQzzm9FtOxT0SLcA5pi01wwcom3u7wxCtc+szD3BE5qLblK9xZW
Ec4M4dc6KDySIGz3E0QaX7GIzdECAwEAAaOB7TCB6jAdBgNVHQ4EFgQUYarNozI3
UWIW3vg1RTWhmPS4UPIwgboGA1UdIwSBsjCBr4AUYarNozI3UWIW3vg1RTWhmPS4
UPKhgZOkgZAwgY0xCzAJBgNVBAYTAkdCMRQwEgYDVQQIDAtPeGZvcmRzaGlyZTEP
MA0GA1UECgwGU29waG9zMQwwCgYDVQQLDANOU0cxJjAkBgNVBAMMHVNvcGhvcyBT
U0wgQ0FfQzQwMDVDTTdNRjJEVjI4MSEwHwYJKoZIhvcNAQkBFhJzdXBwb3J0QHNv
cGhvcy5jb22CAQEwDAYDVR0TBAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAQEAEuSV
vSjfaA2WKeZu84ongK7GQNyx2vrUL62tyCSQnZwLQX5tx/Vh7PtZj+dKuECc4ACa
QXTtwjYgfd6Dw7xQG+y2K1mEp0bd6KRQqBmQ06Dg6m0b9WSsZl9YUpO4uHzz/eST
rkS64ea+5wc7KS1DSZprLJo1/HBGHW2/OsuAD1UOOs9RAo8YoCbOspwA6csJkzA9
Rr+nbtudBLKsNQZ238c/NMS0k5ubBHZNn9KpR8PvZMtr7NNBhDDa07Ig5pd6GoKF
F3g75sBm3aAvENgrsusiWp0ySCnHOlxdC420gAZHc5GrZwA8yL6+US/p17rpmne2
z4tL0zxewjsO54UAYg==
-----END CERTIFICATE-----
"""

cert = ""

if DUMB_DUMB_MODE:
    print("IN SCHOOL MODE")
    time.sleep(2)
    print("installing using bypass")
    DEBUG_MODE = True
    cert = "--cert " + LOCAL_PATH + "/cert"
    with open(os.path.split(sys.executable)[0] + r"\Lib\site-packages\pip\_vendor\certifi\cacert.pem", "r") as file:
        cacert = file.read()

    cacert = SCHOOL_BYPASS_CACERT + "\n" + cacert

    with open(LOCAL_PATH + "/cert", "w") as file:
        file.write(cacert)

try:
    import selenium
except ModuleNotFoundError:
    print("Installing selenium")
    os.system(sys.executable + f" -m pip install selenium {cert}> NULL")
    print("Selenium installed")

try:
    import requests
except ModuleNotFoundError:
    print("Installing requests")
    os.system(sys.executable + f" -m pip install requests {cert}> NULL")

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


def xor_bytes(bytes_1, bytes_2):
    if len(bytes_2) < len(bytes_1):
        bytes_1, bytes_2 = bytes_2, bytes_1

    return bytes(a ^ b for a, b in zip(bytes_1, bytes_2))


def salt_and_hash(password, salt):
    password = hashlib.sha256(password.encode()).digest()
    password = xor_bytes(password, salt)
    password = hashlib.sha256(password).digest()
    return password


def wait_for_change(driver, from_url):
    page = from_url

    while True:
        time.sleep(1)

        new_page = driver.current_url

        if new_page == page:
            continue

        if new_page == "about:blank":
            continue

        return new_page


def render_templated(heading, content):
    web_page = """<style>
    div {
        padding: 32px;
        background-color: white;
        border: black 1px solid;
        border-radius: 8px;
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%)
    }
    h1 {
        margin: 0 0 8px 0;
    }
    body {
        background-color: rgb(220 220 220);
    }
</style>
<div><h1>WIKIRace</h1>
    <h2>{{ heading }}</h2>
    <p>{{ content }}</p>
</div>
""".replace("{{ heading }}", heading). \
        replace("{{ content }}", content). \
        replace("\r\n", ""). \
        replace("\n", ""). \
        replace("    ", "")

    with open(f"{LOCAL_PATH}/WIKIRaceRenderer.temp.html", "w") as file:
        file.write(web_page)

    return f"file:///{LOCAL_PATH}/WIKIRaceRenderer.temp.html"


def render_login():
    web_page = """
<style>
    .divy h1 {
        margin: 0 0 8px 0;
    }

    .divy table {
        width: 100%;
        border-collapse: collapse;
    }

    .divy {
        padding: 32px;
        background-color: white;
        border: black 1px solid;
        border-radius: 8px;
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%)
    }

    body {
        background-color: grey;
    }

    .background {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
    }

    .background img {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        opacity: 0;
        transition: opacity 1s ease-in-out;
    }

    .background img.active {
        opacity: 0.2;
    }
</style>
<div class="background">
    <img src="http://static.wikirace.actorp.us/background_1.PNG" alt="Image 1">
    <img src="http://static.wikirace.actorp.us/background_2.PNG" alt="Image 2">
    <img src="http://static.wikirace.actorp.us/background_3.PNG" alt="Image 3">
    <img src="http://static.wikirace.actorp.us/background_4.PNG" alt="Image 4">
    <img src="http://static.wikirace.actorp.us/background_5.PNG" alt="Image 5">
</div>
<script>
    const images = document.querySelectorAll('.background img');
    let index = Math.floor(Math.random() * images.length);

    images[index].classList.add('active');

    setInterval(() => {
        images[index].classList.remove('active');
        index = (index + 1) % images.length;
        images[index].classList.add('active');
    }, 5000);
</script>
<div class="divy">
    <h1>WIKIRace</h1>
    <form style="align-content: center">
        <table>
            <tr>
                <td>
                    <label for="server">Server IP:</label>
                </td>
                <td>
                    <input type="text" name="server" id="server" placeholder="server.wikirace.actorp.us" value="192.168.56.1">
                </td>
            </tr>
            <tr>
                <td>
                    <label for="port">Server Port:</label>
                </td>
                <td>
                    <input type="text" name="port" id="port" placeholder="37126" value="16124">
                </td>
            </tr>
            <tr id="password_row" style="display:none">
                <td>
                    <label for="password">Server Password:</label>
                </td>
                <td>
                    <input type="password" name="password" id="password">
                </td>
            </tr>
            <tr>
                <td>
                    <label for="name">Name:</label>
                </td>
                <td>
                    <input type="text" name="name" id="name" required maxlength="16" minlength="3">
                </td>
            </tr>
            <tr>
                <td>
                    <label for="password_tick">Password </label>
                    <input type="checkbox" name="password_tick" id="password_tick">
                </td>
                <td>
                    <button type="submit">Submit</button>
                </td>
            </tr>
        </table>
    </form>
    <script>
        const passwordToggle = document.querySelector('#password_tick');
        const passwordRow = document.querySelector('#password_row');

        passwordToggle.addEventListener('change', () => {
            if (passwordToggle.checked) {
                passwordRow.style.display = 'table-row';
            } else {
                passwordRow.style.display = 'none';
            }
        });
    </script>
</div>
""".replace("\r\n", "").replace("\n", "").replace("    ", "")

    with open(f"{LOCAL_PATH}\\WIKIRaceRenderer.temp.html", "w") as file:
        file.write(web_page)

    return f"file:///{LOCAL_PATH}/WIKIRaceRenderer.temp.html"


class Background(threading.Thread):
    def __init__(self, sock):
        super(Background, self).__init__()
        self.deamon = True

        self._sock: socket.SocketType = sock
        self._last_heartbeat = time.time()
        self._server_last_heartbeat = time.time()
        self._sync = False
        self._sync_time = 0
        self._server_time = 0
        self._game_start = False

        self.running = True

    def wait_for_game_start(self):
        while not self._game_start:
            ...

        return

    def _recv(self, data):
        if data == b"HART":
            self._server_last_heartbeat = time.time()
            print(f" [ \033[0;35mS\033[0;0m ] Server has acknowledged our existence")

            return

        if data == b"TMPK":
            print(f" [ \033[0;35mS\033[0;0m ] TimeKeep received")
            self._sync_time = time.time()
            t = self._sock.recv(6)
            t = int.from_bytes(t, 'big') / (2 ** 16)
            self._server_time = t
            self._sync = True

            return

        if data == b"STRT":
            print(f" [ \033[0;35mS\033[0;0m ] Server has started the game")
            self._game_start = True
            return

        print(f" [ \033[0;35mS\033[0;0m ] Client ({self.name}) sent a bad packet, {data=}")

    def sync_time(self):
        start = time.time()

        self._sock.send(b"TMPK")

        while not self._sync:
            time.sleep(0.1)

        ping = (self._sync_time - start) / 2

        self._server_time += ping

        return self._server_time - start

    def run(self) -> None:
        while self.running:
            # only attempt to recv for 1 seconds
            self._sock.settimeout(1)

            try:
                self._recv(self._sock.recv(4))

            except socket.timeout:
                ...

            except ConnectionResetError:
                print(f" \033[0;31m[ \033[0;35mS\033[0;0m \033[0;31m]\033[0;0m Client ({self.name}) has closed there socket, assuming the worst")
                self.running = False
                continue

            self._sock.settimeout(None)

            t = time.time()

            if t > self._last_heartbeat + 10:
                print(f" [ \033[0;35mS\033[0;0m ] HeartBeat out of date, sending new one")
                self._sock.send(b"HART")
                self._last_heartbeat = t


def main():
    print(" [ \033[0;36mM\033[0;0m ] Loading the firefox binary and webdriver...")
    if DUMB_DUMB_MODE:
        driver = webdriver.Chrome()
        print(" [ \033[0;36mM\033[0;0m ] WARNING, in school mode, attempting to launch in chrome")

    else:
        binary = FirefoxBinary(r"C:\Program Files\Mozilla Firefox\firefox.exe")

        driver = webdriver.Firefox(firefox_binary=binary)

    driver.maximize_window()

    print(" [ \033[0;36mM\033[0;0m ] Forcing page update, login")

    page = render_login()
    driver.get(page)
    print(" [ \033[0;36mM\033[0;0m ] waiting for user to input server details")

    new_page = wait_for_change(driver, page)

    data = dict([_.split("=") for _ in
                 new_page.split("file:///" + LOCAL_PATH + "/WIKIRaceRenderer.temp.html?")[1].split("&")])

    server = data["server"]
    port = int(data["port"])
    name = data["name"][:16].ljust(3, "A").ljust(16, "_")

    password = "default"

    if "password_tick" in data:
        password = data["password"]

    print(" [ \033[0;36mM\033[0;0m ] Forcing page update, waiting for server")
    page = render_templated("Please wait for the server to acknowledge your existence",
                            f"connecting to <small>{name.replace('_', '')}@</small><b>{server}</b>:{port}<small>#{password}</small>")
    driver.get(page)

    print(f" [ \033[0;36mM\033[0;0m ] information from the client, {server=} {port=} name={name.replace('_', '')} {password=}")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server, int(port)))

    time.sleep(1)

    client_socket.send(b"JOIN")

    data = client_socket.recv(4)

    if data != b"CNTU":
        page = render_templated("Whoops!",
                                f"Bad server")
        driver.get(page)
        time.sleep(5)
        driver.close()
        sys.exit(-1)

    data = client_socket.recv(1)

    server_has_password = bool(data[0])

    if server_has_password:
        salt = client_socket.recv(32)

        print(f" [ \033[0;36mM\033[0;0m ] Server has a password, using {salt=}")

    client_socket.send(b"NAME")
    client_socket.send(name.encode())

    if server_has_password:
        password = salt_and_hash(password, salt)
        client_socket.send(b"PSWD")
        client_socket.send(password)

    client_socket.send(b"REDY")

    data = client_socket.recv(4)

    if data != b"WAIT":
        page = render_templated("Whoops!",
                                f"Server said nope.<br>Probably a bad password.")
        driver.get(page)
        time.sleep(5)
        driver.close()
        sys.exit(-1)

    print(" [ \033[0;36mM\033[0;0m ] Forcing page update, waiting for game to start")
    page = render_templated("Waiting for game to start",
                            "When the game starts you will be shown a preview of your target<br>"
                            "Then as soon as the first page loads your off!")
    driver.get(page)

    print(" [ \033[0;36mM\033[0;0m ] Connected to server, starting heartbeat")
    # move all socket stuff to a separate thread, now only heartbeat, start, and end.
    background = Background(client_socket)
    background.start()

    print(" [ \033[0;36mM\033[0;0m ] Waiting for server to start the game")
    background.wait_for_game_start()

    print(" [ \033[0;36mM\033[0;0m ] Server has started, syncing times")
    # stalling
    difference = background.sync_time()
    print("time difference,", difference)

    # data = ""
    # while not data:
    #     data = client_socket.recv(1024)
    #
    # data = json.loads(data.decode())
    #
    # start = data["start_point"]
    # end = data["end_point"]
    # start_time = data["start_time"]
    #
    # print("Forcing page update, pre-game")
    # page = render_templated("The game is about to begin", "Give the following page a good read, it is your target page")
    # driver.get(page)
    # time.sleep(10)
    #
    # print("Forcing page update, search, endpoint")
    # page = f"https://en.wikipedia.org/wiki/Special:Search?search={end['article'].replace(' ', '_')}"
    # driver.get(page)
    # time.sleep(5)
    # end = driver.current_url
    #
    # print("starting second thread")
    # wfw = WFW(client_socket)
    # wfw.start()
    #
    # print("Requesting time")
    # current_time = request_time_from_ntp()
    # print("Time from server", current_time)
    # print("Waiting for start time! approx", start_time - current_time, "seconds")
    # time.sleep(start_time - current_time)
    #
    # print("Forcing page update, game pretence")
    # page = render_templated("Prepare to start the game", "it will begin shortly")
    # driver.get(page)
    # time.sleep(5)
    #
    # page = f"https://en.wikipedia.org/wiki/Special:Search?search={start['article'].replace(' ', '_')}"
    # driver.get(page)
    #
    # time.sleep(1)
    # start = driver.current_url
    #
    # current = wait_for_change(driver, page)
    # page = driver.current_url
    #
    # path = [page]
    #
    # while (current != end) and not wfw.gameover:
    #     while not wfw.gameover:
    #         time.sleep(0.1)
    #
    #         new_page = driver.current_url
    #         if new_page == page:
    #             continue
    #
    #         if new_page == "about:blank":
    #             continue
    #
    #         current = new_page
    #         break
    #
    #     page = driver.current_url
    #
    #     path.append(page)
    #
    #     if "://en.wikipedia.org/wiki" not in page:
    #         page = start
    #         driver.get(page)
    #
    # if wfw.gameover:
    #     page = render_templated("Wayyyy... you loose", "the winner took this path <br><br>" + "<br>".join(
    #         [t.split("/wiki/")[1].replace("_", " ") for t in wfw.path]))
    #
    #     driver.get(page)
    #     time.sleep(30)
    #     driver.close()
    #
    # else:
    #     page = render_templated("Congratulations! You win", "let us just inform the others...")
    #     driver.get(page)
    #
    #     client_socket.send(b"WIN")
    #     time.sleep(1)
    #     client_socket.send(json.dumps(path).encode())
    #
    #     time.sleep(5)
    #
    #     driver.close()
    #     wfw.running = False


if DEBUG_MODE:
    print(" [ \033[0;32mG\033[0;0m ] Debug mode enabled, skipping update")

else:
    print(" [ \033[0;32mG\033[0;0m ] Checking client hash...")

    with open(__file__, "rb") as file:
        local_hash = hashlib.sha1(file.read()).hexdigest()

    remote_hash = requests.get(UPDATE_SERVER + "client_hash").text.strip()

    if local_hash != remote_hash:
        print(f" [ \033[0;32mG\033[0;0m ] Bad Client Hash, {local_hash=} {remote_hash=}")
        req = requests.get(UPDATE_SERVER + "WIKIRace.py")

        with open(__file__, "w") as file:
            file.write(req.text)

        sys.exit()

    else:
        print(" [ \033[0;32mG\033[0;0m ] Client chilling, continuing as usual")

if __name__ == '__main__':
    main()
