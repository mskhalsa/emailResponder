# app/scheduler.py
from collections import defaultdict, deque
from typing import List, Dict, Set, Optional
from models import Email

class EmailScheduler:
    def __init__(self, emails: List[Email]):
        self.graph: Dict[str, List[str]] = defaultdict(list)    # parent → [dependents]
        self.in_degree: Dict[str, int] = defaultdict(int)       # email_id → # of unresolved deps
        self.email_map: Dict[str, Email] = {}                   # email_id → Email object
        self.ready_queue: deque[str] = deque()                  # email_ids ready to send

        self._build_graph(emails)

    def _build_graph(self, emails: List[Email]):
        for email in emails:
            self.email_map[email.email_id] = email
            if not email.dependencies:
                self.ready_queue.append(email.email_id)
            for dep in email.dependencies:
                self.graph[dep].append(email.email_id)
                self.in_degree[email.email_id] += 1

    def get_ready_email(self) -> Optional[Email]:
        """Returns next ready-to-send email or None."""
        if not self.ready_queue:
            return None
        eid = self.ready_queue.popleft()
        return self.email_map[eid]

    def mark_completed(self, email_id: str):
        """Notify scheduler that email has been responded to."""
        for dependent in self.graph[email_id]:
            self.in_degree[dependent] -= 1
            if self.in_degree[dependent] == 0:
                self.ready_queue.append(dependent)

    def has_pending(self) -> bool:
        return bool(self.ready_queue)
