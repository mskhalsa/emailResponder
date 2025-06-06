from dataclasses import dataclass, field
from typing import List

@dataclass
class Email:
    email_id: str
    subject: str
    body: str
    deadline: float  # seconds from GET time
    dependencies: List[str] = field(default_factory=list)
