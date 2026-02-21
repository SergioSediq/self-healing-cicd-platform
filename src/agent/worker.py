"""Background worker for heal jobs. Run: python worker.py"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.queue import dequeue

def main():
    while True:
        job = dequeue()
        if job:
            run_id = job.get("run_id", "unknown")
            provider = job.get("provider", "local")
            logs = job.get("logs") or ""
            args = ["--run-id", run_id, "--provider", provider]
            if logs:
                args.extend(["--logs", logs[:50000]])
            import subprocess
            subprocess.run([sys.executable, "main.py"] + args, cwd=os.path.dirname(os.path.abspath(__file__)))
        else:
            time.sleep(2)

if __name__ == "__main__":
    main()
