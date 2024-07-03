import requests
import json

data = {
    "Name": "Ашан",
    "City": "Ульяновск",
    "Street": "Минаева",
    "House": 99,
    "Open_Time": "6:00:00",
    "Close_Time": "10:00:00"}

Store = json.dumps(data)

response = requests.post("http://127.0.0.1:8000/shop", data=Store)
print(response.text)