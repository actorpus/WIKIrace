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

DEBUG_MODE = False
UPDATE_SERVER = "https://raw.githubusercontent.com/actorpus/WIKIrace/main/"
LOCAL_PATH = sys.path[0].replace("\\", "/")
REF_TIME_1970 = 2208988800


# https://stackoverflow.com/questions/36500197/how-to-get-time-from-an-ntp-server
def request_time_from_ntp(addr="0.de.pool.ntp.org"):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = b'\x1b' + 47 * b'\0'
    client.sendto(data, (addr, 123))
    data, address = client.recvfrom(1024)
    if data:
        t = struct.unpack("!12I", data)[10]
        t -= REF_TIME_1970

    return t


def wait_for_change(driver, from_url):
    page = from_url
    if DEBUG_MODE: print("looking for deviations from", page)

    while True:
        time.sleep(1)

        new_page = driver.current_url
        if DEBUG_MODE: print("looking at", new_page)

        if new_page == page:
            continue

        if new_page == "about:blank":
            continue

        if DEBUG_MODE: print("deviation detected")

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
    <h1>WIKIRace</h1>
    <form style="align-content: center">
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

    with open(f"{LOCAL_PATH}\\WIKIRaceRenderer.temp.html", "w") as file:
        file.write(web_page)

    return f"file:///{LOCAL_PATH}/WIKIRaceRenderer.temp.html"


class WFW(threading.Thread):
    def __init__(self, sock):
        super(WFW, self).__init__()

        self.sock = sock
        self.gameover = False
        self.path = []

        self.deamon = True
        self.running = True

    def run(self) -> None:
        while self.running:
            data = b""
            while not data:
                data = self.sock.recv(16_384)

            data = json.loads(data)

            if DEBUG_MODE: print(data)

            if "gameover" in data:
                self.gameover = True
                self.path = data["path"]

                self.running = False


def main():
    print("Loading the firefox binary and webdriver...")
    binary = FirefoxBinary(r"C:\Program Files\Mozilla Firefox\firefox.exe")

    driver = webdriver.Firefox(firefox_binary=binary)

    print("Forcing page update, login")

    page = render_login()
    driver.get(page)
    print("waiting for user to input server details")

    new_page = wait_for_change(driver, page)

    server, port, name = [_.split("=")[1] for _ in new_page.split(
        "file:///" + LOCAL_PATH + "/WIKIRaceRenderer.temp.html?"
    )[1].split("&")]

    print("Forcing page update, waiting for server")
    page = render_templated("Please wait for the server to acknowledge your existence",
                            f"connecting to {server}:{port}")
    driver.get(page)

    print(f"information from the client, {server=} {port=} {name=}")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server, int(port)))

    time.sleep(1)

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
    page = render_templated("Waiting for game to start",
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
    page = render_templated("The game is about to begin", "Give the following page a good read, it is your target page")
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
    current_time = request_time_from_ntp()
    print("Time from server", current_time)
    print("Waiting for start time! approx", start_time - current_time, "seconds")
    time.sleep(start_time - current_time)

    print("Forcing page update, game pretence")
    page = render_templated("Prepare to start the game", "it will begin shortly")
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
        page = render_templated("Wayyyy... you loose", "the winner took this path <br><br>" + "<br>".join(
            [t.split("/wiki/")[1].replace("_", " ") for t in wfw.path]))

        driver.get(page)
        time.sleep(30)
        driver.close()

    else:
        page = render_templated("Congratulations! You win", "let us just inform the others...")
        driver.get(page)

        client_socket.send(b"WIN")
        time.sleep(1)
        client_socket.send(json.dumps(path).encode())

        time.sleep(5)

        driver.close()
        wfw.running = False


if DEBUG_MODE:
    print("Debug mode enabled, skipping update")

else:
    print("Checking client hash...")

    with open(__file__, "rb") as file:
        local_hash = hashlib.sha1(file.read()).hexdigest()

    remote_hash = requests.get(UPDATE_SERVER + "client_hash").text.strip()

    if local_hash != remote_hash:
        print(f"Bad Client Hash, {local_hash=} {remote_hash=}")
        req = requests.get(UPDATE_SERVER + "WIKIRace.py")

        with open(__file__, "w") as file:
            file.write(req.text)

        sys.exit()

    else:
        print("Client chilling, continuing as usual")

if __name__ == '__main__':
    main()
