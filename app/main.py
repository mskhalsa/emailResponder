# app/main.py
import time
import threading
import queue
from fetcher import fetch_emails
from models import Email
from utils import get_api_key, is_test_mode
from mock_llm import mock_openai_response
import requests

# Configuration
default_workers = 20  # adjust to number of emails or machine capacity

# Constants
MIN_DEPENDENCY_GAP = 0.0001  # 100 microseconds


def worker(work_queue: queue.Queue, graph: dict, in_degree: dict, email_map: dict,
           in_degree_lock: threading.Lock, completed: set, start_time: float):
    while True:
        try:
            email = work_queue.get_nowait()
        except queue.Empty:
            break

        elapsed = time.time() - start_time
        if elapsed >= email.deadline:
            print(f"❌ Missed deadline for {email.email_id} (elapsed: {elapsed:.2f}s)")
            work_queue.task_done()
            continue

        print(f"💬 Responding to {email.email_id} (deadline: {email.deadline:.2f}s, elapsed: {elapsed:.2f}s)")
        response_text = mock_openai_response(email.subject, email.body)

        payload = {
            "email_id": email.email_id,
            "response_body": response_text,
            "api_key": get_api_key()
        }
        if is_test_mode():
            payload["test_mode"] = "true"

        try:
            res = requests.post(
                "https://9uc4obe1q1.execute-api.us-east-2.amazonaws.com/dev/responses",
                json=payload,
                timeout=3
            )
            res.raise_for_status()
            print(f"✅ Responded to {email.email_id}")
            completed.add(email.email_id)
        except Exception as e:
            print(f"🚨 Failed to POST response for {email.email_id}: {e}")

        time.sleep(MIN_DEPENDENCY_GAP)

        # Unlock dependents
        with in_degree_lock:
            for child_id in graph.get(email.email_id, []):
                in_degree[child_id] -= 1
                if in_degree[child_id] == 0:
                    work_queue.put(email_map[child_id])

        work_queue.task_done()


def main():
    print("📥 Fetching emails...")
    emails = fetch_emails(api_key=get_api_key(), test_mode=is_test_mode())
    print(f"📨 Fetched {len(emails)} emails")
    start_time = time.time()

    # Build graph, in_degree map, and email lookup
    graph = {e.email_id: [] for e in emails}
    in_degree = {e.email_id: 0 for e in emails}
    email_map = {e.email_id: e for e in emails}

    for e in emails:
        for dep in e.dependencies:
            graph.setdefault(dep, []).append(e.email_id)
            in_degree[e.email_id] += 1

    # Prepare work queue with initial ready emails
    work_queue = queue.Queue()
    for eid, deg in in_degree.items():
        if deg == 0:
            work_queue.put(email_map[eid])

    in_degree_lock = threading.Lock()
    completed = set()

    # Start worker threads
    threads = []
    num_workers = min(default_workers, len(emails))
    for _ in range(num_workers):
        t = threading.Thread(target=worker,
                             args=(work_queue, graph, in_degree, email_map, in_degree_lock, completed, start_time))
        t.start()
        threads.append(t)

    # Wait for all work to be done
    for t in threads:
        t.join()

    print(f"\n✅ Done. Responded to {len(completed)} out of {len(emails)} emails.")


if __name__ == "__main__":
    main()
