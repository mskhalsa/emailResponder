# app/main.py

import time
from fetcher import fetch_emails
from scheduler import EmailScheduler
from responder import respond_to_email
from utils import get_api_key, is_test_mode

def main():
    # Step 1: Start clock and fetch emails
    emails = fetch_emails(api_key=get_api_key(), test_mode=is_test_mode())
    print(f"📨 Fetched {len(emails)} emails")
    start_time = time.time()
    print("📥 Fetching emails...")

    # Step 2: Build DAG and initialize scheduler
    scheduler = EmailScheduler(emails)

    # Step 3: Task loop — keep processing until nothing left
    completed = set()
    while scheduler.has_pending():
        email = scheduler.get_ready_email()
        if not email:
            continue  # wait for something to unlock

        success = respond_to_email(email, start_time)

        if success:
            completed.add(email.email_id)
            scheduler.mark_completed(email.email_id)
        else:
            print(f"⚠️ Skipping downstream dependencies for {email.email_id} due to deadline miss")

    print(f"\n✅ Done. Responded to {len(completed)} out of {len(emails)} emails.")

if __name__ == "__main__":
    main()
