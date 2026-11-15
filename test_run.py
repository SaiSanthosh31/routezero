import sys
import os
import time
import threading
import uvicorn
import importlib.util

# Load target app
target_path = os.path.abspath(os.path.join("target-app", "main.py"))
spec_target = importlib.util.spec_from_file_location("target_module", target_path)
target_module = importlib.util.module_from_spec(spec_target)
spec_target.loader.exec_module(target_module)

target_thread = threading.Thread(
    target=lambda: uvicorn.run(target_module.app, host='127.0.0.1', port=8001, log_level='error'),
    daemon=True
)
target_thread.start()
time.sleep(1)

# Load backend
backend_dir = os.path.abspath("backend")
sys.path.insert(0, backend_dir)

import main as backend_main
from db.database import get_all_findings, get_all_endpoints

print("Starting autonomous DAST scan against target app...")
backend_main.run_dast_scan_workflow()

endpoints = get_all_endpoints()
findings = get_all_findings()

print("\n==========================================")
print(f"Discovered Endpoints: {len(endpoints)}")
for ep in endpoints:
    print(f"  [{ep['category'].upper()}] {ep['method']} {ep['path']}")

print(f"\nConfirmed Vulnerabilities: {len(findings)}")
for f in findings:
    print(f"  [{f['severity']}] {f['title']}")
    print(f"    Path: {f['endpoint']}")
    print(f"    Proof: {f['reproduction_curl']}")
print("==========================================\n")
