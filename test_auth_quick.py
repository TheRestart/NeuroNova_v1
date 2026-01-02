#!/usr/bin/env python
"""Quick OpenEMR OAuth2 authentication test"""

import requests
import json

# Configuration
TOKEN_URL = "http://localhost:80/oauth2/default/token"
CLIENT_ID = "neuronova-cdss-internal"
CLIENT_SECRET = "8fa14ca80a5e67dd19625d743ef5bb60"

print("=" * 60)
print("OpenEMR OAuth2 Quick Test")
print("=" * 60)
print(f"Token URL: {TOKEN_URL}")
print(f"Client ID: {CLIENT_ID}")
print(f"Client Secret: {CLIENT_SECRET[:10]}...")
print()

try:
    print("[1/2] Requesting Access Token...")
    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10
    )

    print(f"  Status Code: {response.status_code}")

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        print(f"  [SUCCESS] Access Token: {access_token[:30]}...")
        print(f"  Token Type: {token_data.get('token_type')}")
        print(f"  Expires In: {token_data.get('expires_in')} seconds")
        print()

        # Test FHIR API
        print("[2/2] Testing FHIR API (Patient list)...")
        fhir_url = "http://localhost:80/apis/default/fhir/Patient"
        fhir_response = requests.get(
            fhir_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/fhir+json"
            },
            timeout=10
        )

        print(f"  Status Code: {fhir_response.status_code}")

        if fhir_response.status_code == 200:
            bundle = fhir_response.json()
            total = bundle.get("total", 0)
            print(f"  [SUCCESS] Retrieved {total} patients")
            print()
            print("=" * 60)
            print("[RESULT] All tests passed!")
            print("=" * 60)
        else:
            print(f"  [FAILED] FHIR API Error")
            print(f"  Response: {fhir_response.text}")

    else:
        print(f"  [FAILED] Token request failed")
        print(f"  Response: {response.text}")

except Exception as e:
    print(f"[ERROR] {e}")

