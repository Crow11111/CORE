import time
import requests
import json

def benchmark(model_name, prompt="Erzähle einen kurzen Witz"):
    url = "http://localhost:11436/api/generate"
    data = {
        "model": model_name,
        "prompt": prompt,
        "stream": True
    }
    
    print(f"Starte Benchmark für {model_name}...")
    start_time = time.time()
    first_token_time = None
    full_response = ""
    
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=data, headers=headers, stream=True)
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                if first_token_time is None:
                    first_token_time = time.time() - start_time
                full_response += chunk.get("response", "")
                if chunk.get("done"):
                    break
        
        total_time = time.time() - start_time
        return {
            "model": model_name,
            "ttft": first_token_time,
            "total_time": total_time,
            "response_length": len(full_response),
            "response": full_response
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Teste gemma2:2b und gemma2:9b
    for m in ["gemma2:2b", "gemma2:9b"]:
        print(f"\n--- Benchmark für {m} (Kalt-Start) ---")
        res_cold = benchmark(m)
        print(json.dumps(res_cold, indent=2))
        
        print(f"\n--- Benchmark für {m} (Warm-Start) ---")
        res_warm = benchmark(m)
        print(json.dumps(res_warm, indent=2))
