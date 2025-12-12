#!/usr/bin/env python3
"""Test script to explore CBORG API endpoints."""

import os
import json
import requests
from openai import OpenAI

API_KEY = os.environ.get('CBORG_API_KEY')
BASE_URL = 'https://api.cborg.lbl.gov'

if not API_KEY:
    print("Error: CBORG_API_KEY environment variable not set")
    exit(1)

print(f"API Key: {API_KEY[:8]}...{API_KEY[-4:]}")
print(f"Base URL: {BASE_URL}")
print("\n" + "="*60)

# Test 1: Get models list using OpenAI SDK
print("\n1. Testing /v1/models endpoint (OpenAI SDK):")
try:
    client = OpenAI(api_key=API_KEY, base_url=f"{BASE_URL}/v1")
    models = client.models.list()
    print(f"✓ Found {len(models.data)} models")
    print("\nFirst 10 models:")
    for i, model in enumerate(models.data[:10]):
        print(f"  {i+1}. {model.id}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: Get user info
print("\n" + "="*60)
print("\n2. Testing /user/info endpoint:")
try:
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(f"{BASE_URL}/user/info", headers=headers)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: Try alternate endpoints
print("\n" + "="*60)
print("\n3. Testing /v1/usage endpoint:")
try:
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(f"{BASE_URL}/v1/usage", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "="*60)
print("\nTest complete!")
