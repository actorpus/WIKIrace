import requests
import hashlib
import time
import json
import socket
import sys
import os

try:
    import selenium
except ModuleNotFoundError:
    print("Installing selenium")
    os.system(sys.executable + " -m pip install selenium > NULL")
    print("Selenium installed")

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


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
    return f'data:text/html,<div style="padding: 32px; border: black 1px solid; position: absolute; left: 50%; ' \
           f'top: 50%; transform: translate(-50%, -50%)"><h1>WIKI races</h1><h2>{heading}</h2><p>{content}</p></div>'


def main():
    binary = FirefoxBinary(r"C:\Program Files\Mozilla Firefox\firefox.exe")

    driver = webdriver.Firefox(firefox_binary=binary)

    default = """
<div style="padding: 32px; border: black 1px solid; position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%)">
    <h1>WIKI races</h1>
    <form style="align-content: center" action="http://local/">
        <label for="server">Server IP:</label>
        <input type="text" name="server" id="server" placeholder="192.168.56.7" value="192.168."><br>
        <label for="port">Server Port:</label>
        <input type="text" name="port" id="port" placeholder="37126" value="37126"><br>
        <label for="name">Name:</label>
        <input type="text" name="name" id="name" placeholder="Joe"><br>
        <button type="submit">Submit</button>
    </form>
</div>
""".replace("\r\n", "").replace("\n", "").replace("    ", "")

    page = f"data:text/html,{default}"
    driver.get(page)
    print("waiting for user to input server details")

    new_page = wait_for_change(driver, page)

    server, port, name = [_.split("=")[1] for _ in new_page.split("http://local/?")[1].split("&")]

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

    page = render("Waiting for game to start", "When the game starts you will be shown a preview of your target<br>Then as soon as the first page loads your off!")
    driver.get(page)

    data = ""
    while not data:
        data = client_socket.recv(1024)

    data = json.loads(data.decode())

    start = data["start_point"]
    end = data["end_point"]

    page = render("Loading target preview...", "Navigating around this page is pointless")
    driver.get(page)
    time.sleep(2)

    page = f"https://en.wikipedia.org/wiki/Special:Search?search={end['article'].replace(' ', '_')}"
    driver.get(page)
    time.sleep(10)

    end = driver.current_url
    page = render("Prepare to start the game", "it will begin shortly")
    driver.get(page)
    time.sleep(2)

    page = f"https://en.wikipedia.org/wiki/Special:Search?search={start['article'].replace(' ', '_')}"
    driver.get(page)

    time.sleep(1)
    start = driver.current_url

    current = wait_for_change(driver, page)
    page = driver.current_url

    path = [page]

    while current != end:
        current = wait_for_change(driver, page)
        page = driver.current_url

        path.append(page)

        if "://en.wikipedia.org/wiki" not in page:
            page = start
            driver.get(page)

    # driver.get("data:text/html,<h1>You Win</h1>")
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
