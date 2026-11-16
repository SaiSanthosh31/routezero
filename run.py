import subprocess
import sys
import time
import os
import webbrowser

def main():
    print("=" * 60)
    print("🚀 Starting RouteZero — Autonomous Travel API DAST Platform")
    print("=" * 60)

    # 1. Start Target Travel App (Port 8001)
    target_cmd = [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8001"]
    print("-> Launching Target B2B Travel App on http://127.0.0.1:8001...")
    target_proc = subprocess.Popen(target_cmd, cwd=os.path.abspath("target-app"))

    time.sleep(1.5)

    # 2. Start RouteZero DAST Core API & Frontend (Port 8000)
    backend_cwd = os.path.abspath("backend") if os.path.exists("backend") else os.path.abspath(".")
    backend_cmd = [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"]
    print("-> Launching RouteZero DAST Engine on http://127.0.0.1:8000...")
    backend_proc = subprocess.Popen(backend_cmd, cwd=backend_cwd)

    time.sleep(1.5)

    print("\n✅ Platform Ready!")
    print("   🌐 Dashboard:   http://127.0.0.1:8000")
    print("   🎯 Target API:  http://127.0.0.1:8001/docs")
    print("\nPress Ctrl+C to stop both servers.\n")

    try:
        # Open in default browser automatically
        webbrowser.open("http://127.0.0.1:8000")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping services...")
        target_proc.terminate()
        backend_proc.terminate()
        print("Shutdown complete.")

if __name__ == "__main__":
    main()
