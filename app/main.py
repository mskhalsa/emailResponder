import time
from concurrent.futures import ThreadPoolExecutor
from fetcher import fetch_emails
from scheduler import EmailScheduler
from responder import respond_to_email
from utils import get_api_key, is_test_mode

def main():
    print("Fetching emails...")
    emails = fetch_emails(api_key=get_api_key(), test_mode=is_test_mode())
    print(f"Fechthed {len(emails)} emails")
    start_time = time.time()

    scheduler = EmailScheduler(emails)
    completed = set()
    in_progress = set()

    with ThreadPoolExecutor(max_workers=1000) as executor:
        futures = {}

        while True:
            while scheduler.has_pending():
                email = scheduler.get_ready_email()
                if email and email.email_id not in in_progress:
                    
                    # skip low priority emails
                    if email.deadline < 0.3:
                        continue

                    future = executor.submit(respond_to_email, email, start_time)
                    futures[future] = email
                    in_progress.add(email.email_id)

            # Check for completed responses
            done = [f for f in futures if f.done()]
            for f in done:
                email = futures.pop(f)
                in_progress.remove(email.email_id)
                try:
                    success = f.result()
                    if success:
                        completed.add(email.email_id)
                        scheduler.mark_completed(email.email_id)
                except Exception as e:
                    print(f"Exception while responding to {email.email_id}: {e}")

            if not scheduler.has_pending() and not futures:
                break

            time.sleep(0.001) 

    print(f"\nResponded to {len(completed)} out of {len(emails)} emails.")

if __name__ == "__main__":
    main()
