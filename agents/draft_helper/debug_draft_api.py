import requests
import json
import base64

url = "http://localhost:8013/draft"
payload = {
    "requirements": "Draft a simple NDA for a software developer.",
    "user_context": "Testing API"
}

try:
    print(f"Sending request to {url}...")
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("Response Keys:", data.keys())
        print("File Name:", data.get("file_name"))
        
        b64 = data.get("document_base64")
        if b64:
            print(f"Base64 Length: {len(b64)}")
            print(f"Base64 Start: {b64[:50]}")
            
            # Try to decode
            try:
                decoded = base64.b64decode(b64)
                print(f"Decoded Bytes Length: {len(decoded)}")
                print("Header bytes (hex):", decoded[:10].hex())
                # Zip signature is 50 4b 03 04
                if decoded[:4].hex() == "504b0304":
                    print("VALID ZIP HEADER DETECTED (DOCX is a zip)")
                else:
                    print("INVALID ZIP HEADER")
            except Exception as e:
                print(f"Base64 Decode Error: {e}")
        else:
            print("No document_base64 found.")
    else:
        print("Error Response:", response.text)

except Exception as e:
    print(f"Connection Error: {e}")
