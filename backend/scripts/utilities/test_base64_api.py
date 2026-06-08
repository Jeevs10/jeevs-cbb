#!/usr/bin/env python3
"""Test script for segmentation API with base64 image data."""
import requests
import json
import base64

# Read sample image and encode as base64
image_path = "/Users/sanjiv/jeevs-cbb/backend/data/sample_image.png"
with open(image_path, "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")

# Test with base64 data
url = "http://localhost:8000/api/v1/segmentation"
payload = {
    "image_data": image_data
}

print(f"Testing segmentation API with base64 image data...")
print(f"URL: {url}")
print(f"Base64 data length: {len(image_data)} characters")

try:
    response = requests.post(url, json=payload, timeout=120)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        print(f"\nSuccess! Response keys: {response.json().keys()}")
    else:
        print(f"\nError! Response:")
        print(response.text)
except Exception as e:
    print(f"\nException occurred: {e}")
