import time
import requests
from mock_llm import mock_openai_response
from models import Email
from utils import get_api_key, is_test_mode

min_gap = 0.0001  # 100 microsencods

def respond_to_email(email: Email, start_time: float) -> bool:
    elapsed = time.time() - start_time
    if elapsed >= email.deadline:
        print(f"Missed deadline for {email.email_id} (elapsed: {elapsed:.2f}s)")
        return False

    print(f"Responding to {email.email_id} (deadline: {email.deadline:.2f}s, elapsed: {elapsed:.2f}s)")

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
            timeout=5
        )
        res.raise_for_status()
        print(f"Responded to {email.email_id}")
    except Exception as e:
        print(f"Failed to POST response for {email.email_id}: {e}")
        return False

    time.sleep(min_gap)
    return True
