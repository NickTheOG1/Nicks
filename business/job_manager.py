"""Job Manager - Manages pickup jobs, scheduling, and tracking"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class Job:
    \"\"\"Represents a job/pickup\"\"\"
    job_id: str
    customer_id: str
    lot_number: str
    location: str
    equipment_type: str
    status: str  # new, scheduled, in_progress, completed, cancelled
    pickup_date: Optional[datetime] = None
    pickup_window: Optional[str] = None  # e.g., \"9am-12pm\"
    assigned_rigger: Optional[str] = None
    assigned_truck: Optional[str] = None
    amount: float = 0.0
    paid: bool = False
    notes: str = \"\"
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

    def __repr__(self):
        return f\"<Job {self.lot_number} - {self.status}>\"


class JobManager:
    \"\"\"Manages all jobs for the business\"\"\"

    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self.job_counter = 0

    def create_job(self, customer_id: str, lot_number: str, location: str,
                   equipment_type: str, notes: str = \"\") -> Job:
        \"\"\"Create a new job\"\"\"
        self.job_counter += 1
        job_id = f\"JOB-{self.job_counter:05d}\"

        job = Job(
            job_id=job_id,
            customer_id=customer_id,
            lot_number=lot_number,
            location=location,
            equipment_type=equipment_type,
            status='new',
            notes=notes,
        )

        self.jobs[job_id] = job
        logger.info(f\"Created job: {job_id} - Lot {lot_number}\")
        return job

    def schedule_pickup(self, job_id: str, pickup_date: datetime, pickup_window: str,
                       rigger: Optional[str] = None, truck: Optional[str] = None) -> bool:
        \"\"\"Schedule a pickup for a job\"\"\"
        if job_id not in self.jobs:
            logger.warning(f\"Job {job_id} not found\")
            return False

        job = self.jobs[job_id]
        job.pickup_date = pickup_date
        job.pickup_window = pickup_window
        job.assigned_rigger = rigger
        job.assigned_truck = truck
        job.status = 'scheduled'

        logger.info(f\"Scheduled pickup for {job_id}: {pickup_date} {pickup_window}\")
        return True

    def update_job_status(self, job_id: str, status: str) -> bool:
        \"\"\"Update job status\"\"\"
        if job_id not in self.jobs:
            return False

        self.jobs[job_id].status = status
        logger.info(f\"Updated {job_id} status to {status}\")
        return True

    def mark_job_completed(self, job_id: str, amount: float) -> bool:
        \"\"\"Mark job as completed and set amount\"\"\"
        if job_id not in self.jobs:
            return False

        job = self.jobs[job_id]
        job.status = 'completed'
        job.amount = amount
        logger.info(f\"Completed {job_id}: ${amount:.2f}\")
        return True

    def mark_job_paid(self, job_id: str) -> bool:
        \"\"\"Mark job as paid\"\"\"
        if job_id not in self.jobs:
            return False

        self.jobs[job_id].paid = True
        logger.info(f\"Marked {job_id} as paid\")
        return True

    def get_upcoming_pickups(self, days: int = 7) -> List[Job]:
        \"\"\"Get upcoming pickups for next N days\"\"\"
        today = datetime.utcnow().date()
        upcoming = []

        for job in self.jobs.values():
            if job.status == 'scheduled' and job.pickup_date:
                if today <= job.pickup_date.date() <= (today + timedelta(days=days)):
                    upcoming.append(job)

        return sorted(upcoming, key=lambda x: x.pickup_date)

    def get_unscheduled_jobs(self) -> List[Job]:
        \"\"\"Get jobs that haven't been scheduled yet\"\"\"
        return [job for job in self.jobs.values() if job.status == 'new']

    def get_unpaid_jobs(self) -> List[Job]:
        \"\"\"Get completed but unpaid jobs\"\"\"
        return [job for job in self.jobs.values()
                if job.status == 'completed' and not job.paid]

    def get_job_summary(self) -> Dict[str, Any]:
        \"\"\"Get summary of all jobs\"\"\"
        jobs = list(self.jobs.values())
        return {
            'total_jobs': len(jobs),
            'new': len([j for j in jobs if j.status == 'new']),
            'scheduled': len([j for j in jobs if j.status == 'scheduled']),
            'in_progress': len([j for j in jobs if j.status == 'in_progress']),
            'completed': len([j for j in jobs if j.status == 'completed']),
            'total_revenue': sum(j.amount for j in jobs if j.completed),
            'unpaid_amount': sum(j.amount for j in jobs if j.status == 'completed' and not j.paid),
        }
