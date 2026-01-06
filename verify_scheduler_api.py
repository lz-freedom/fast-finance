import requests
import time
import sys

BASE_URL = "http://localhost:9130/api/v1/scheduler"

def wait_for_server():
    print("Waiting for server to start...")
    for i in range(10):
        try:
            resp = requests.get("http://localhost:9130/docs")
            if resp.status_code == 200:
                print("Server is up!")
                return True
        except:
            pass
        time.sleep(2)
    return False

def verify():
    if not wait_for_server():
        print("[FAIL] Server failed to start")
        sys.exit(1)

    print("\n=== Verifying Scheduler API ===")
    
    # 1. List Jobs
    print("1. Testing GET /jobs")
    resp = requests.get(f"{BASE_URL}/jobs")
    if resp.status_code != 200:
        print(f"[FAIL] GET /jobs failed: {resp.status_code} {resp.text}")
        sys.exit(1)
        
    data = resp.json().get("data", [])
    print(f"[OK] Got {len(data)} jobs")
    job_ids = [j["id"] for j in data]
    print(f"Job IDs: {job_ids}")
    
    expected = ["yahoo_sync_morning", "yahoo_sync_evening", "tradingview_sync_morning"]
    for ex in expected:
        if ex not in job_ids:
            print(f"[FAIL] Expected job {ex} not found")
    
    # 2. Get Job Details
    target_id = "yahoo_sync_morning"
    print(f"\n2. Testing GET /jobs/{target_id}")
    resp = requests.get(f"{BASE_URL}/jobs/{target_id}")
    if resp.status_code != 200:
        print(f"[FAIL] GET /jobs/{target_id} failed: {resp.status_code}")
    else:
        job_info = resp.json().get("data")
        if job_info["id"] == target_id:
            print(f"[OK] Job details verified for {target_id}")
        else:
            print(f"[FAIL] Job ID mismatch")

    # 3. Simulate Run (Trigger)
    # Note: Running actual sync might be heavy. We just check if endpoint responds 200.
    # We won't actually trigger it if we want to avoid side effects? 
    # Actually user might want to see if it works. 
    # But sync is heavy. Let's just pause/resume.
    
    # 3. Pause
    print(f"\n3. Testing POST /jobs/{target_id}/pause")
    resp = requests.post(f"{BASE_URL}/jobs/{target_id}/pause")
    if resp.status_code == 200:
        print("[OK] Pause successful")
    else:
        print(f"[FAIL] Pause failed: {resp.text}")

    # 4. Resume
    print(f"\n4. Testing POST /jobs/{target_id}/resume")
    resp = requests.post(f"{BASE_URL}/jobs/{target_id}/resume")
    if resp.status_code == 200:
        print("[OK] Resume successful")
    else:
        print(f"[FAIL] Resume failed: {resp.text}")

    print("\n5. Testing Static Dashboard")
    resp = requests.get("http://localhost:9130/static/scheduler.html")
    if resp.status_code == 200:
        print("[OK] Dashboard accessible")
    else:
        print(f"[FAIL] Dashboard missing: {resp.status_code}")

    print("\n=== Verification Complete ===")

if __name__ == "__main__":
    verify()
