"""
Background job scheduler for workspace cleanup and maintenance tasks.
"""

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import Settings
from app.core.database import SessionLocal
from app.services.email_service import EmailService
from app.services.file_storage import FileStorage
from app.services.workspace_cleanup_service import WorkspaceCleanupService

logger = logging.getLogger(__name__)


class CleanupScheduler:
    """Scheduler for workspace cleanup jobs."""

    def __init__(self, settings: Settings):
        """
        Initialize scheduler.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.scheduler = BackgroundScheduler()

    def cleanup_job(self) -> None:
        """
        Run workspace cleanup job.

        This job:
        1. Sends warning emails to owners of workspaces nearing deletion
        2. Deletes workspaces that have exceeded retention period
        3. Sends deletion confirmation emails
        """
        logger.info("Starting workspace cleanup job")

        try:
            # Create database session
            db = SessionLocal()

            try:
                # Initialize services
                email_service = EmailService(
                    smtp_host=self.settings.smtp_host,
                    smtp_port=self.settings.smtp_port,
                    from_email=self.settings.from_email,
                    smtp_user=self.settings.smtp_user,
                    smtp_password=self.settings.smtp_password,
                )

                file_storage = FileStorage(settings=self.settings)

                cleanup_service = WorkspaceCleanupService(
                    db=db,
                    settings=self.settings,
                    email_service=email_service,
                    file_storage=file_storage,
                )

                # Run cleanup
                stats = cleanup_service.run_cleanup()

                logger.info(
                    f"Workspace cleanup completed: "
                    f"{stats['warnings_sent']} warnings sent, "
                    f"{stats['workspaces_deleted']} workspaces deleted"
                )
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error during workspace cleanup: {str(e)}", exc_info=True)

    def start(self) -> None:
        """Start the scheduler."""
        if not self.settings.cleanup_job_enabled:
            logger.info("Cleanup job is disabled")
            return

        # Parse cron expression
        cron_parts = self.settings.cleanup_job_cron.split()
        if len(cron_parts) != 5:
            logger.error(f"Invalid cron expression: {self.settings.cleanup_job_cron}")
            return

        minute, hour, day, month, day_of_week = cron_parts

        # Add cleanup job
        self.scheduler.add_job(
            self.cleanup_job,
            trigger=CronTrigger(
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week,
            ),
            id="workspace_cleanup",
            name="Workspace Cleanup Job",
            replace_existing=True,
        )

        self.scheduler.start()
        logger.info(f"Cleanup scheduler started with cron: {self.settings.cleanup_job_cron}")

    def shutdown(self) -> None:
        """Shutdown the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Cleanup scheduler stopped")


# Global scheduler instance
_scheduler: CleanupScheduler | None = None


def get_scheduler(settings: Settings) -> CleanupScheduler:
    """
    Get or create the global scheduler instance.

    Args:
        settings: Application settings

    Returns:
        CleanupScheduler instance
    """
    global _scheduler
    if _scheduler is None:
        _scheduler = CleanupScheduler(settings)
    return _scheduler
