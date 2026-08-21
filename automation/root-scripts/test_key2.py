import os
import requests
import json

api_key = os.getenv("GEMINI_API_KEY", "")
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
payload = {
    "contents": [{"parts": [{"text": "Hello, are you working?"}]}]
}
response = requests.post(url, json=payload)
print(response.status_code)
print(response.text)
