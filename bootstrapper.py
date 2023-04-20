import requests, hashlib, sys
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