import time
import threading
import numpy as np

# List of possible responses to cycle through.
responses = [
    "Thank you for your email. I will get back to you shortly.",
    "I appreciate your message, and I'll respond as soon as possible.",
    "Your inquiry has been received. I'll review it and reply soon.",
    "Thanks for reaching out. Expect a detailed response shortly.",
]

# Global counter to cycle through the responses.
response_counter = 0

def mock_openai_response(subject: str, body: str) -> str:
    """
    Simulates an API response by waiting for a delay sampled from an exponential
    distribution (with mean 0.5 seconds) that is bounded between 0.4 and 0.6 seconds,
    and then returning a response message starting with "Re: {subject}".
    
    Args:
        subject (str): The subject of the email.
        body (str): The body of the email (currently not used in generating the response).

    Returns:
        str: The formatted email response.
    """
    global response_counter
    # Generate a delay from an exponential distribution with mean 0.5 seconds.
    delay = np.random.exponential(scale=0.5)
    # Bound the delay between 0.4 and 0.6 seconds.
    delay = max(0.4, min(delay, 0.6))
    time.sleep(delay)

    # Cycle through the list of responses.
    response_text = responses[response_counter % len(responses)]
    response_counter += 1

    # Return the response with the email subject prefixed.
    return f"Re: {subject}\n\n{response_text}"
