from collections import defaultdict, deque
from typing import List, Dict, Set, Optional
from models import Email

class EmailScheduler:
    def __init__(self, emails: List[Email]):
        self.graph: Dict[str, List[str]] = defaultdict(list) 
        self.in_degree: Dict[str, int] = defaultdict(int)    
        self.email_map: Dict[str, Email] = {}                
        self.ready_queue: deque[str] = deque()               

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
        if not self.ready_queue:
            return None
        eid = self.ready_queue.popleft()
        return self.email_map[eid]

    def mark_completed(self, email_id: str):
        for dependent in self.graph[email_id]:
            self.in_degree[dependent] -= 1
            if self.in_degree[dependent] == 0:
                self.ready_queue.append(dependent)

    def has_pending(self) -> bool:
        return bool(self.ready_queue)
