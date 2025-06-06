import requests
from models import Email

def fetch_emails(api_key: str, test_mode: bool = True) -> list[Email]:
    base_url = "https://9uc4obe1q1.execute-api.us-east-2.amazonaws.com/dev/emails"
    params = {"api_key": api_key}
    if test_mode:
        params["test_mode"] = "true"

    res = requests.get(base_url, params=params)
    res.raise_for_status()
    raw = res.json()

    return [
        Email(
            email_id=e["email_id"],
            subject=e["subject"],
            body=e["body"],
            deadline=float(e["deadline"]),
            dependencies=[d.strip() for d in e["dependencies"].split(",") if d.strip()]
        )
        for e in raw
    ]
