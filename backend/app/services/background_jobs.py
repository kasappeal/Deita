"""
Background job service for workspace cleanup and maintenance tasks.
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID
from enum import Enum


class JobStatus(Enum):
    """Status of background jobs."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class BackgroundJob:
    """Represents a background job."""
    
    def __init__(
        self,
        job_id: str,
        job_type: str,
        payload: Dict[str, Any],
        scheduled_at: Optional[datetime] = None,
        max_retries: int = 3
    ):
        self.job_id = job_id
        self.job_type = job_type
        self.payload = payload
        self.status = JobStatus.PENDING
        self.scheduled_at = scheduled_at or datetime.utcnow()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error_message: Optional[str] = None
        self.retry_count = 0
        self.max_retries = max_retries


class WorkspaceCleanupJob:
    """Background job for workspace cleanup operations."""
    
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory
        self.job_queue: List[BackgroundJob] = []
        self.running_jobs: Dict[str, BackgroundJob] = {}
    
    async def schedule_orphan_cleanup(self) -> str:
        """Schedule cleanup of expired orphan workspaces."""
        job_id = f"orphan_cleanup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        job = BackgroundJob(
            job_id=job_id,
            job_type="orphan_cleanup",
            payload={},
            scheduled_at=datetime.utcnow(),
        )
        self.job_queue.append(job)
        return job_id
    
    async def schedule_inactive_workspace_cleanup(self, days_inactive: int = 60) -> str:
        """Schedule cleanup of inactive owned workspaces."""
        job_id = f"inactive_cleanup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        job = BackgroundJob(
            job_id=job_id,
            job_type="inactive_cleanup",
            payload={"days_inactive": days_inactive},
            scheduled_at=datetime.utcnow(),
        )
        self.job_queue.append(job)
        return job_id
    
    async def schedule_expiration_warnings(self) -> str:
        """Schedule sending expiration warnings."""
        job_id = f"expiration_warnings_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        job = BackgroundJob(
            job_id=job_id,
            job_type="expiration_warnings",
            payload={},
            scheduled_at=datetime.utcnow(),
        )
        self.job_queue.append(job)
        return job_id
    
    async def schedule_audit_log_cleanup(self) -> str:
        """Schedule cleanup of old audit logs based on retention policy."""
        job_id = f"audit_cleanup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        job = BackgroundJob(
            job_id=job_id,
            job_type="audit_cleanup",
            payload={},
            scheduled_at=datetime.utcnow(),
        )
        self.job_queue.append(job)
        return job_id
    
    async def process_jobs(self):
        """Process pending jobs in the queue."""
        while self.job_queue:
            job = self.job_queue.pop(0)
            
            if datetime.utcnow() < job.scheduled_at:
                # Job not ready yet, put it back
                self.job_queue.append(job)
                continue
            
            try:
                await self._execute_job(job)
            except Exception as e:
                await self._handle_job_failure(job, str(e))
    
    async def _execute_job(self, job: BackgroundJob):
        """Execute a specific job."""
        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        self.running_jobs[job.job_id] = job
        
        try:
            if job.job_type == "orphan_cleanup":
                result = await self._execute_orphan_cleanup()
            elif job.job_type == "inactive_cleanup":
                result = await self._execute_inactive_cleanup(job.payload["days_inactive"])
            elif job.job_type == "expiration_warnings":
                result = await self._execute_expiration_warnings()
            elif job.job_type == "audit_cleanup":
                result = await self._execute_audit_cleanup()
            else:
                raise ValueError(f"Unknown job type: {job.job_type}")
            
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.payload["result"] = result
            
        except Exception as e:
            job.error_message = str(e)
            raise
        finally:
            self.running_jobs.pop(job.job_id, None)
    
    async def _execute_orphan_cleanup(self) -> Dict[str, Any]:
        """Execute orphan workspace cleanup."""
        # Placeholder implementation
        # In real implementation, would use WorkspaceCleanupService
        deleted_count = 0
        
        # Simulate cleanup logic
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        # Would query database and delete expired orphan workspaces
        # deleted_count = await cleanup_service.cleanup_expired_workspaces()
        
        return {
            "deleted_workspaces": deleted_count,
            "cutoff_date": cutoff_date.isoformat(),
        }
    
    async def _execute_inactive_cleanup(self, days_inactive: int) -> Dict[str, Any]:
        """Execute inactive workspace cleanup."""
        deleted_count = 0
        cutoff_date = datetime.utcnow() - timedelta(days=days_inactive)
        
        # Would query database and delete inactive workspaces
        # deleted_count = await cleanup_service.cleanup_inactive_owned_workspaces(days_inactive)
        
        return {
            "deleted_workspaces": deleted_count,
            "days_inactive": days_inactive,
            "cutoff_date": cutoff_date.isoformat(),
        }
    
    async def _execute_expiration_warnings(self) -> Dict[str, Any]:
        """Execute expiration warning notifications."""
        warnings_sent = 0
        
        # Would query workspaces expiring soon and send notifications
        # warnings_sent = await cleanup_service.send_expiration_warnings()
        
        return {
            "warnings_sent": warnings_sent,
        }
    
    async def _execute_audit_cleanup(self) -> Dict[str, Any]:
        """Execute audit log cleanup based on retention policy."""
        deleted_logs = 0
        
        # Would clean up audit logs older than retention period (7 years)
        cutoff_date = datetime.utcnow() - timedelta(days=365 * 7)
        
        return {
            "deleted_logs": deleted_logs,
            "cutoff_date": cutoff_date.isoformat(),
        }
    
    async def _handle_job_failure(self, job: BackgroundJob, error: str):
        """Handle job failure and retry logic."""
        job.retry_count += 1
        job.error_message = error
        
        if job.retry_count < job.max_retries:
            job.status = JobStatus.RETRYING
            # Exponential backoff: 2^retry_count minutes
            retry_delay = 2 ** job.retry_count
            job.scheduled_at = datetime.utcnow() + timedelta(minutes=retry_delay)
            self.job_queue.append(job)
        else:
            job.status = JobStatus.FAILED
            job.completed_at = datetime.utcnow()
        
        # Log the failure
        await self._log_job_failure(job, error)
    
    async def _log_job_failure(self, job: BackgroundJob, error: str):
        """Log job failure for monitoring and debugging."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "job_id": job.job_id,
            "job_type": job.job_type,
            "error": error,
            "retry_count": job.retry_count,
            "status": job.status.value,
        }
        # In real implementation, would send to logging system
        print(f"Job failed: {log_entry}")
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific job."""
        # Check running jobs
        if job_id in self.running_jobs:
            job = self.running_jobs[job_id]
            return self._job_to_dict(job)
        
        # Check queued jobs
        for job in self.job_queue:
            if job.job_id == job_id:
                return self._job_to_dict(job)
        
        return None
    
    def _job_to_dict(self, job: BackgroundJob) -> Dict[str, Any]:
        """Convert job to dictionary for API responses."""
        return {
            "job_id": job.job_id,
            "job_type": job.job_type,
            "status": job.status.value,
            "scheduled_at": job.scheduled_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "retry_count": job.retry_count,
            "max_retries": job.max_retries,
            "error_message": job.error_message,
        }


class ScheduledJobManager:
    """Manager for scheduled recurring jobs."""
    
    def __init__(self, cleanup_job_service: WorkspaceCleanupJob):
        self.cleanup_service = cleanup_job_service
        self.is_running = False
    
    async def start_scheduler(self):
        """Start the job scheduler."""
        self.is_running = True
        
        # Schedule regular jobs
        await self._schedule_recurring_jobs()
        
        # Process jobs in background
        asyncio.create_task(self._job_processor())
    
    async def stop_scheduler(self):
        """Stop the job scheduler."""
        self.is_running = False
    
    async def _schedule_recurring_jobs(self):
        """Schedule all recurring jobs."""
        # Daily orphan cleanup
        await self.cleanup_service.schedule_orphan_cleanup()
        
        # Weekly inactive workspace cleanup
        await self.cleanup_service.schedule_inactive_workspace_cleanup(60)
        
        # Daily expiration warnings
        await self.cleanup_service.schedule_expiration_warnings()
        
        # Monthly audit log cleanup
        await self.cleanup_service.schedule_audit_log_cleanup()
    
    async def _job_processor(self):
        """Background job processor."""
        while self.is_running:
            try:
                await self.cleanup_service.process_jobs()
                # Sleep for 1 minute between job processing cycles
                await asyncio.sleep(60)
            except Exception as e:
                print(f"Error in job processor: {e}")
                await asyncio.sleep(60)  # Continue processing even if there's an error


# Global instances (would be properly configured with dependency injection in real app)
cleanup_job_service = WorkspaceCleanupJob(None)  # Would pass proper DB session factory
scheduled_job_manager = ScheduledJobManager(cleanup_job_service)