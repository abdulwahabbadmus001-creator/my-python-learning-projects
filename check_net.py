import requests

try:
    response = requests.get("https://www.google.com", timeout=5)
    print("Success! Connected to the internet. Status code:", response.status_code)
except Exception as e:
    print("Connection failed:", e)
