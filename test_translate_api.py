import requests
import json

# Test the translation endpoint directly
url = "http://localhost:5000/api/translate"

# Test data - same as what the frontend sends
data = {
    "text": "welcome to polyglot pal",
    "source": "en",
    "target": "hi"
}

print("Testing translation API...")
print(f"URL: {url}")
print(f"Data: {json.dumps(data, indent=2)}")
print()

try:
    # Make the request (need to be logged in, so this might fail)
    response = requests.post(url, json=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print()
    
    if response.status_code == 200:
        result = response.json()
        print("SUCCESS!")
        print(f"Original: {result.get('original')}")
        print(f"Translated: {result.get('translated')}")
        print(f"Source Lang: {result.get('src_lang')}")
        print(f"Target Lang: {result.get('dest_lang')}")
    else:
        print("FAILED!")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()


