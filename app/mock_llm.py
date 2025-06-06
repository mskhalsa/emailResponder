# app/mock_llm.py

import time
import numpy as np

responses = [
    "Thank you for your email. I will get back to you shortly.",
    "I appreciate your message, and I'll respond as soon as possible.",
    "Your inquiry has been received. I'll review it and reply soon.",
    "Thanks for reaching out. Expect a detailed response shortly.",
]

response_counter = 0

def mock_openai_response(subject: str, body: str) -> str:
    global response_counter
    delay = np.random.exponential(scale=0.5)
    delay = max(0.4, min(delay, 0.6))
    time.sleep(delay)

    response_text = responses[response_counter % len(responses)]
    response_counter += 1
    return f"Re: {subject}\n\n{response_text}"
