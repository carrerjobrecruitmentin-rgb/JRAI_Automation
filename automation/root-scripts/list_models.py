import os
import requests
import json

api_key = os.getenv("GEMINI_API_KEY", "")
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
response = requests.get(url)
print(response.status_code)
print(response.text)
