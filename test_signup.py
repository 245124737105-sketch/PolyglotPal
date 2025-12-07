import requests

# Test signup endpoint
url = "http://localhost:5000/signup"
data = {
    "name": "Test User",
    "email": "test@example.com",
    "password": "password123"
}

print("Testing signup endpoint...")
print(f"URL: {url}")
print(f"Data: {data}")
print()

try:
    response = requests.post(url, data=data, allow_redirects=False)
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
