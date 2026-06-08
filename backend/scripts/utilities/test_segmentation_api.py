#!/usr/bin/env python3
"""Test script for segmentation API."""
import requests
import json

# Test with local file
url = "http://localhost:8000/api/v1/segmentation"
payload = {
    "image_path": "/Users/sanjiv/jeevs-cbb/backend/data/sample_image.png"
}

print(f"Testing segmentation API with local file...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload, timeout=60)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        print(f"\nSuccess! Response:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"\nError! Response:")
        print(response.text)
except Exception as e:
    print(f"\nException occurred: {e}")
