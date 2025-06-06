# app/responder.py
import asyncio
import httpx
from mock_llm import mock_openai_response
from models import Email
from utils import get_api_key, is_test_mode

MIN_DEPENDENCY_GAP = 0.0001  # 100μs

async def respond_to_email(email: Email, start_time: float) -> bool:
    elapsed = asyncio.get_event_loop().time() - start_time
    if elapsed >= email.deadline:
        print(f"❌ Missed deadline for {email.email_id} (elapsed: {elapsed:.2f}s)")
        return False

    print(f"💬 Responding to {email.email_id} (deadline: {email.deadline:.2f}s, elapsed: {elapsed:.2f}s)")

    response_text = await mock_openai_response(email.subject, email.body)

    payload = {
        "email_id": email.email_id,
        "response_body": response_text,
        "api_key": get_api_key()
    }
    if is_test_mode():
        payload["test_mode"] = "true"

    try:
        async with httpx.AsyncClient(timeout=3) as client:
            res = await client.post(
                "https://9uc4obe1q1.execute-api.us-east-2.amazonaws.com/dev/responses",
                json=payload
            )
            res.raise_for_status()
            print(f"✅ Responded to {email.email_id}")
    except Exception as e:
        print(f"🚨 Failed to POST response for {email.email_id}: {e}")
        return False

    await asyncio.sleep(MIN_DEPENDENCY_GAP)
    return True
