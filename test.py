#! python3
import requests

wss = requests.get("https://e9bc-108-147-93-139.ngrok.io:8080", "test")
print(wss)