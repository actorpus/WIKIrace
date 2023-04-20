import threading
import requests
import hashlib
import time
import json
import socket
import sys
import os
import struct

try:
    import selenium
except ModuleNotFoundError:
    print("Installing selenium")
    os.system(sys.executable + " -m pip install selenium > NULL")
    print("Selenium installed")

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


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

    return t


def wait_for_change(driver, from_url):
    page = from_url
    while True:
        time.sleep(0.1)

        new_page = driver.current_url
        if new_page == page:
            continue

        if new_page == "about:blank":
            continue

        return new_page


def render(heading, content):
    return """data:text/html,
<style>
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
<div><h1>WIKI races</h1>
    <h2>{{ heading }}</h2>
    <p>{{ content }}</p>
</div>
""".replace("{{ heading }}", heading). \
        replace("{{ content }}", content). \
        replace("\r\n", ""). \
        replace("\n", ""). \
        replace("    ", "")


class WFW(threading.Thread):
    def __init__(self, sock):
        super(WFW, self).__init__()

        self.sock = sock
        self.gameover = False
        self.path = []

        self.deamon = True

    def run(self) -> None:
        while True:
            data = b""
            while not data:
                data = self.sock.recv(16_384)

            data = json.loads(data)

            print(data)

            if "gameover" in data:
                self.gameover = True
                self.path = data["path"]


def main():
    print("Finding and binding baby")
    binary = FirefoxBinary(r"C:\Program Files\Mozilla Firefox\firefox.exe")

    driver = webdriver.Firefox(firefox_binary=binary)

    print("Forcing page update, login")
    default = """
<style>
    body {
        background-color: rgb(220 220 220);
    }

    h1 {
        margin: 0 0 8px 0;
    }

    table {
        width: 100%;
        border-collapse: collapse;
    }

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
</style>
<div>
    <h1>WIKI races</h1>
    <form style="align-content: center" action="http://local/">
        <table>
            <tr>
                <td>
                    <label for="server">Server IP:</label>
                </td>
                <td>
                    <input type="text" name="server" id="server" placeholder="192.168.56.7" value="169.254.217.82"><br>
                </td>
            </tr>
            <tr>
                <td>
                    <label for="port">Server Port:</label>
                </td>
                <td>
                    <input type="text" name="port" id="port" placeholder="37126" value="37126"><br>
                </td>
            </tr>
            <tr>
                <td>
                    <label for="name">Name:</label>
                </td>
                <td>
                    <input type="text" name="name" id="name" placeholder="Joe"><br>
                </td>
            </tr>
            <tr>
                <td></td>
                <td>
                    <button type="submit">Submit</button>
                </td>
            </tr>
        </table>
    </form>
</div>
""".replace("\r\n", "").replace("\n", "").replace("    ", "")

    page = f"data:text/html,{default}"
    driver.get(page)
    print("waiting for user to input server details")

    new_page = wait_for_change(driver, page)

    server, port, name = [_.split("=")[1] for _ in new_page.split("http://local/?")[1].split("&")]

    print("Forcing page update, waiting for server")
    page = render("Please wait for the server to acknowledge your existence", f"connecting to {server}:{port}")
    driver.get(page)

    print("information from the client... server", server, "port", port)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server, int(port)))

    time.sleep(2)

    welcome_message = {
        "name": name,
    }

    client_socket.send(json.dumps(welcome_message).encode())

    data = ""
    while not data:
        data = client_socket.recv(1024)

    if data != b"WELCOME":
        print(data)
        print("bad server")
        driver.close()
        sys.exit(-1)

    print("Forcing page update, waiting for game to start")
    page = render("Waiting for game to start",
                  "When the game starts you will be shown a preview of your target<br>"
                  "Then as soon as the first page loads your off!")
    driver.get(page)

    data = ""
    while not data:
        data = client_socket.recv(1024)

    data = json.loads(data.decode())

    start = data["start_point"]
    end = data["end_point"]
    start_time = data["start_time"]

    print("Forcing page update, pre-game")
    page = render("The game is about to begin", "Give the following page a good read, it is your target page")
    driver.get(page)
    time.sleep(10)

    print("Forcing page update, search, endpoint")
    page = f"https://en.wikipedia.org/wiki/Special:Search?search={end['article'].replace(' ', '_')}"
    driver.get(page)
    time.sleep(5)
    end = driver.current_url

    print("starting second thread")
    wfw = WFW(client_socket)
    wfw.start()

    print("Requesting time")
    current_time = RequestTimefromNtp()
    print("Time from server", current_time)
    print("Waiting for start time! approx", start_time - current_time, "seconds")
    time.sleep(start_time - current_time)

    print("Forcing page update, game pretence")
    page = render("Prepare to start the game", "it will begin shortly")
    driver.get(page)
    time.sleep(5)

    page = f"https://en.wikipedia.org/wiki/Special:Search?search={start['article'].replace(' ', '_')}"
    driver.get(page)

    time.sleep(1)
    start = driver.current_url

    current = wait_for_change(driver, page)
    page = driver.current_url

    path = [page]

    while (current != end) and not wfw.gameover:
        # current = wait_for_change(driver, page)
        while not wfw.gameover:
            time.sleep(0.1)

            new_page = driver.current_url
            if new_page == page:
                continue

            if new_page == "about:blank":
                continue

            current = new_page
            break

        page = driver.current_url

        path.append(page)

        if "://en.wikipedia.org/wiki" not in page:
            page = start
            driver.get(page)

    if wfw.gameover:
        page = render("Wayyyy... you loose", "the winner took this path <br><br>" + "<br>".join([t.split("/wiki/")[1].replace("_", " ") for t in wfw.path]))
        driver.get(page)
        time.sleep(30)
        driver.close()

    else:
        page = render("Congratulations! You win", "let us just inform the others...")
        driver.get(page)

        client_socket.send(b"WIN")
        time.sleep(1)
        client_socket.send(json.dumps(path).encode())

        time.sleep(5)

        driver.close()


print("Checking client hash...")
with open(__file__, "rb") as file: hsh = hashlib.sha1(file.read()).hexdigest()
phsh = requests.get("https://raw.githubusercontent.com/actorpus/WIKIraces/main/client_hash").text.strip()
if hsh != phsh:
    print(f"Bad Client Hash, {hsh=} {phsh=}")
    req = requests.get("https://raw.githubusercontent.com/actorpus/WIKIraces/main/WIKIraces.py")
    with open(__file__, "w") as file: file.write(req.text)
    sys.exit()
else:
    print("Client chilling")

if __name__ == '__main__':
    main()
