"""
Quick script to test and discover your backend's API format
Run this to figure out the exact payload structure your backend expects

File: FortiPrompt/test_backend_api.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("="*60)
print("TESTING YOUR RAG BACKEND API")
print("="*60)

# Test 1: Check if backend is responding
print("\n[Test 1] Checking backend connectivity...")
try:
    # Try FastAPI docs endpoint
    response = requests.get(f"{BASE_URL}/docs", timeout=3)
    print(f"✓ Backend is running (status: {response.status_code})")
    print(f"  FastAPI docs available at: {BASE_URL}/docs")
except Exception as e:
    print(f"✗ Cannot connect: {e}")
    print("  Make sure your backend is running on port 8000")
    exit(1)

# Test 2: Try to get OpenAPI schema to see endpoints
print("\n[Test 2] Fetching API endpoints...")
try:
    response = requests.get(f"{BASE_URL}/openapi.json", timeout=3)
    if response.status_code == 200:
        openapi = response.json()
        print("✓ Available endpoints:")
        for path, methods in openapi.get("paths", {}).items():
            for method in methods.keys():
                print(f"  {method.upper():6} {path}")
except Exception as e:
    print(f"⚠ Could not fetch OpenAPI schema: {e}")

# Test 3: Try different payload formats for /chat endpoint
print("\n[Test 3] Testing /chat endpoint with different payloads...")

test_payloads = [
    {
        "name": "Format 1: query + model_id",
        "payload": {
            "query": "What is the company policy on vacation?",
            "model_id": "Llama31"
        }
    },
    {
        "name": "Format 2: query + model + conversation_id",
        "payload": {
            "query": "What is the company policy on vacation?",
            "model_id": "Llama31",
            "conversation_id": "test123"
        }
    },
    {
        "name": "Format 3: message instead of query",
        "payload": {
            "message": "What is the company policy on vacation?",
            "model_id": "Llama31"
        }
    },
    {
        "name": "Format 4: Simple query only",
        "payload": {
            "query": "What is the company policy on vacation?"
        }
    }
]

working_format = None

for test in test_payloads:
    print(f"\n  Testing: {test['name']}")
    print(f"  Payload: {json.dumps(test['payload'], indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json=test['payload'],
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            print("  ✓ SUCCESS!")
            data = response.json()
            print(f"  Response structure: {list(data.keys())}")
            
            # Print first 200 chars of response
            response_text = str(data.get('response', data.get('answer', data)))[:200]
            print(f"  Response preview: {response_text}...")
            
            working_format = test
            break
        else:
            error = response.text[:200]
            print(f"  ✗ Failed: {error}")
            
    except Exception as e:
        print(f"  ✗ Error: {e}")

# Test 4: Save working format
if working_format:
    print("\n" + "="*60)
    print("✓ FOUND WORKING FORMAT!")
    print("="*60)
    print("\nUse this payload structure in your FortiPrompt integration:")
    print(json.dumps(working_format['payload'], indent=2))
    
    # Save to file
    with open("working_backend_format.json", "w") as f:
        json.dump({
            "endpoint": "/chat",
            "method": "POST",
            "payload": working_format['payload'],
            "description": working_format['name']
        }, f, indent=2)
    
    print("\n✓ Saved to: working_backend_format.json")
    
else:
    print("\n" + "="*60)
    print("✗ NO WORKING FORMAT FOUND")
    print("="*60)
    print("\nPlease check your backend's API documentation")
    print(f"Visit: {BASE_URL}/docs")
    print("\nOr check your main.py file for the exact endpoint structure")

# Test 5: List available models
print("\n[Test 4] Checking available models...")
try:
    # Your backend showed: ['Gpt4', 'Gemini', 'Claude', 'Llama31', 'Mistral', 'Qwen']
    print("Available models from your logs:")
    print("  - Gpt4")
    print("  - Gemini")
    print("  - Claude")
    print("  - Llama31")
    print("  - Mistral")
    print("  - Qwen")
except Exception as e:
    print(f"Could not list models: {e}")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
print("\nNext steps:")
print("1. Check the working format above")
print("2. Update target_interface.py with correct payload structure")
print("3. Run: python core/target_interface.py")