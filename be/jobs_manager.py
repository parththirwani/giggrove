from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict
import threading  # Use threading lock for synchronous code

@dataclass
class Event: 
    timestamp: datetime
    data: str

@dataclass
class Job: 
    status: str
    events: List[Event]
    result: str

# Use threading.Lock for synchronous code
jobs_lock = threading.Lock()
jobs: Dict[str, Job] = {}

def append_event(job_id: str, event_data: str):
    with jobs_lock:
        if job_id not in jobs:
            print(f"Start job: {job_id}")
            jobs[job_id] = Job(
                status="STARTED",
                events=[],
                result=""
            )
        print(f"Appending to job: {job_id}")
        jobs[job_id].events.append(
            Event(
                timestamp=datetime.now(),
                data=event_data
            )
        )
