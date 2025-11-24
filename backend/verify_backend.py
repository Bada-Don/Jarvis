import requests

try:
    # Test Chat
    response = requests.post('http://localhost:5000/api/chat', json={'message': 'Hello from Python'})
    print("Chat Response:", response.json())

    # Test Upload
    with open('test_upload.txt', 'rb') as f:
        response = requests.post('http://localhost:5000/api/upload', files={'file': f})
    print("Upload Response:", response.json())

except Exception as e:
    print("Error:", e)
