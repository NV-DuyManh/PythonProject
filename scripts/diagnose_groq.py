import os
import sys
import json
import urllib.request
import urllib.error
import time

def diagnose_groq():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("ERROR: GROQ_API_KEY environment variable not set.")
        sys.exit(1)
        
    print("GROQ API KEY LOADED.")
    print("TESTING /models ENDPOINT...")
    
    req = urllib.request.Request("https://api.groq.com/openai/v1/models")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("User-Agent", "Mozilla/5.0")
    
    models = []
    try:
        with urllib.request.urlopen(req) as response:
            status = response.getcode()
            print(f"HTTP Status: {status}")
            data = json.loads(response.read().decode())
            for model in data.get("data", []):
                models.append(model["id"])
                print(f"  - {model['id']} (owned_by: {model.get('owned_by')})")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}")
        print(e.read().decode())
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
        
    print("\n--- CLASSIFYING EXPECTED MODELS ---")
    expected_models = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b"
    ]
    for em in expected_models:
        if em in models:
            print(f"{em}: AVAILABLE")
        else:
            print(f"{em}: NOT_AVAILABLE")

    print("\n--- NATIVE GROQ COMPLETION TEST ---")
    primary_model = None
    for em in expected_models:
        if em in models:
            primary_model = em
            break
            
    if not primary_model:
        print("No expected models available. Selecting first available model for native test.")
        if models:
            primary_model = models[0]
        else:
            print("No models returned by Groq.")
            sys.exit(1)
            
    print(f"Selected model for native test: {primary_model}")
    
    payload = json.dumps({
        "model": primary_model,
        "messages": [
            {"role": "system", "content": "You are a concise code reviewer."},
            {"role": "user", "content": "Review this Python function: def add(a,b): return a+b"}
        ],
        "max_tokens": 50
    }).encode("utf-8")
    
    req = urllib.request.Request("https://api.groq.com/openai/v1/chat/completions", data=payload)
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "Mozilla/5.0")
    
    start_time = time.time()
    try:
        with urllib.request.urlopen(req) as response:
            status = response.getcode()
            data = json.loads(response.read().decode())
            latency = time.time() - start_time
            print(f"NATIVE GROQ: PASS")
            print(f"MODEL: {primary_model}")
            print(f"LATENCY: {latency:.2f}s")
    except urllib.error.HTTPError as e:
        print(f"NATIVE GROQ: FAIL (HTTP {e.code})")
        print(e.read().decode())
    except Exception as e:
        print(f"NATIVE GROQ: FAIL ({e})")
        
    print("\n--- LITELLM GROQ TEST ---")
    try:
        from litellm import completion
        start_time = time.time()
        response = completion(
            model=f"groq/{primary_model}",
            messages=[
                {"role": "system", "content": "You are a concise code reviewer."},
                {"role": "user", "content": "Review this Python function: def add(a,b): return a+b"}
            ],
            max_tokens=50
        )
        latency = time.time() - start_time
        print(f"LITELLM GROQ: PASS")
        print(f"MODEL: groq/{primary_model}")
        print(f"LATENCY: {latency:.2f}s")
    except Exception as e:
        print(f"LITELLM GROQ: FAIL")
        print(str(e))
        
if __name__ == "__main__":
    diagnose_groq()
