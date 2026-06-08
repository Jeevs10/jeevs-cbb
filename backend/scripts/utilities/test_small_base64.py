#!/usr/bin/env python3
"""Test script for segmentation API with small base64 image data."""
import requests
import json
import base64

# Read small test image and encode as base64
image_path = "/tmp/small_test.png"
with open(image_path, "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")

# Test with base64 data
url = "http://localhost:8000/api/v1/segmentation"
payload = {
    "image_data": image_data
}

print(f"Testing segmentation API with small base64 image data...")
print(f"URL: {url}")
print(f"Base64 data length: {len(image_data)} characters")

try:
    response = requests.post(url, json=payload, timeout=60)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        print(f"\nSuccess! Response keys: {response.json().keys()}")
        result = response.json()
        if 'result' in result and result['result']:
            print(f"Predictions count: {len(result['result'].get('predictions', []))}")
    else:
        print(f"\nError! Response:")
        print(response.text)
except Exception as e:
    print(f"\nException occurred: {e}")
