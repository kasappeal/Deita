# Workspace Cleanup System

## Overview

The Workspace Cleanup System automatically deletes inactive workspaces to manage storage and maintain system efficiency. It implements different retention policies for orphaned (anonymous) and owned (registered user) workspaces, with email notifications sent to workspace owners before deletion.

## Features

- **Automatic Deletion**: Workspaces are automatically deleted after exceeding their retention period
- **Differential Retention**: Different policies for orphaned vs owned workspaces
- **Email Notifications**: Workspace owners receive warnings before deletion and confirmation after
- **Graceful Handling**: Continues operation even if email sending or file deletion fails
- **Configurable**: All intervals and schedules are configurable via environment variables

## Retention Policies

### Orphaned Workspaces

- **Retention Period**: 15 days (default, configurable)
- **No Warnings**: Anonymous users do not receive email notifications
- **Automatic Deletion**: Deleted silently after retention period expires

### Owned Workspaces

- **Retention Period**: 30 days (default, configurable)
- **Warning Emails**: Sent at 15, 10, 5, 3, and 1 days before deletion (configurable)
- **Deletion Confirmation**: Email sent after workspace is deleted
- **Grace Period**: Accessing the workspace resets the `last_accessed_at` timestamp, canceling scheduled deletion

## How It Works

### 1. Last Access Tracking

The system tracks workspace activity through the `last_accessed_at` timestamp, which is updated when:

- Workspace is accessed via API
- Files are uploaded
- Queries are executed
- Tables are viewed

### 2. Cleanup Job Schedule

A background job runs daily (by default at 2 AM) to:

1. Find workspaces eligible for deletion based on retention policies
2. Send warning emails to owners of workspaces nearing deletion
3. Delete workspaces that have exceeded retention period
4. Clean up associated files from object storage
5. Send deletion confirmation emails

### 3. Deletion Process

When a workspace is deleted:

1. All associated files are deleted from S3-compatible object storage
2. Database records are deleted (workspace, files, queries, chat messages)
3. Deletion is confirmed even if file storage deletion fails
4. Confirmation email is sent to workspace owner (if applicable)

## Configuration

### Environment Variables

Add these to your `backend/.env` file:

```bash
# Retention periods (in days)
ORPHANED_WORKSPACE_RETENTION_DAYS=15
OWNED_WORKSPACE_RETENTION_DAYS=30

# Warning intervals (comma-separated days before deletion)
WORKSPACE_WARNING_INTERVALS=15,10,5,3,1

# Cleanup job schedule (cron expression)
# Format: minute hour day month day_of_week
# Default: daily at 2 AM
CLEANUP_JOB_CRON=0 2 * * *

# Enable/disable automatic cleanup job
CLEANUP_JOB_ENABLED=true
```

### Cron Expression Examples

```bash
# Every day at 2:00 AM
CLEANUP_JOB_CRON=0 2 * * *

# Every day at midnight
CLEANUP_JOB_CRON=0 0 * * *

# Every 6 hours
CLEANUP_JOB_CRON=0 */6 * * *

# Every Sunday at 3:00 AM
CLEANUP_JOB_CRON=0 3 * * 0

# Every day at 2:30 AM
CLEANUP_JOB_CRON=30 2 * * *
```

## Email Notifications

### Warning Email

Sent to workspace owners at configured intervals before deletion. Includes:

- Workspace name and ID
- Number of files
- Storage used
- Days until deletion
- Scheduled deletion date
- Link to access workspace (resets deletion timer)

### Deletion Confirmation Email

Sent after workspace deletion. Includes:

- Workspace name and ID
- Number of files deleted
- Storage freed
- Confirmation that all data has been permanently removed

## Implementation Details

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │               Lifecycle Manager                         │ │
│  │  • Starts scheduler on startup                          │ │
│  │  • Stops scheduler on shutdown                          │ │
│  └────────────────┬───────────────────────────────────────┘ │
│                   │                                           │
│  ┌────────────────▼───────────────────────────────────────┐ │
│  │            CleanupScheduler                             │ │
│  │  • Manages APScheduler background job                   │ │
│  │  • Runs cleanup_job() on cron schedule                  │ │
│  └────────────────┬───────────────────────────────────────┘ │
│                   │                                           │
│  ┌────────────────▼───────────────────────────────────────┐ │
│  │         WorkspaceCleanupService                         │ │
│  │  • Finds workspaces for deletion                        │ │
│  │  • Finds workspaces needing warnings                    │ │
│  │  • Deletes workspaces and files                         │ │
│  │  • Sends email notifications                            │ │
│  └─────┬──────────────────────┬────────────────────────────┘ │
│        │                      │                              │
│  ┌─────▼──────┐      ┌───────▼────────┐                     │
│  │EmailService│      │  FileStorage   │                     │
│  │• Warning   │      │ • Delete files │                     │
│  │• Deletion  │      │   from S3      │                     │
│  └────────────┘      └────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

1. **CleanupScheduler** (`app/core/scheduler.py`)

   - Manages APScheduler background job
   - Configures cron trigger
   - Handles startup/shutdown lifecycle

2. **WorkspaceCleanupService** (`app/services/workspace_cleanup_service.py`)

   - Implements cleanup logic
   - Finds workspaces based on retention policies
   - Manages deletion process
   - Coordinates email notifications

3. **EmailService** (`app/services/email_service.py`)
   - Sends warning emails
   - Sends deletion confirmation emails
   - HTML and plain text templates

### Database Queries

The system uses efficient SQL queries to find workspaces:

```sql
-- Find orphaned workspaces for deletion
SELECT * FROM workspaces
WHERE owner_id IS NULL
AND last_accessed_at < (NOW() - INTERVAL '15 days');

-- Find owned workspaces for deletion
SELECT * FROM workspaces
WHERE owner_id IS NOT NULL
AND last_accessed_at < (NOW() - INTERVAL '30 days');

-- Find workspaces needing warnings (15 days before deletion)
SELECT w.*, u.* FROM workspaces w
JOIN users u ON w.owner_id = u.id
WHERE w.owner_id IS NOT NULL
AND w.last_accessed_at < (NOW() - INTERVAL '15 days')
AND w.last_accessed_at >= (NOW() - INTERVAL '16 days');
```

## Operational Considerations

### Monitoring

Monitor the cleanup job through:

- Application logs: Search for "workspace cleanup" entries
- Database queries: Check `last_accessed_at` distribution
- Email delivery: Monitor SMTP logs for notification delivery

### Troubleshooting

**Cleanup job not running:**

1. Check `CLEANUP_JOB_ENABLED=true` in environment
2. Verify cron expression is valid
3. Check application logs for scheduler errors
4. Ensure FastAPI application started successfully

**Emails not sending:**

- Verify SMTP configuration in environment variables
- Check email service logs
- Note: Cleanup continues even if emails fail (by design)

**Files not being deleted:**

- Check S3/MinIO connectivity
- Verify S3 credentials and bucket access
- Note: Workspace deletion continues even if file deletion fails

### Testing in Development

For testing purposes, you can use shorter retention periods:

```bash
# Test with short retention (minutes instead of days)
ORPHANED_WORKSPACE_RETENTION_DAYS=0.0104  # ~15 minutes
OWNED_WORKSPACE_RETENTION_DAYS=0.0208    # ~30 minutes
WORKSPACE_WARNING_INTERVALS=0.0104,0.007,0.0035,0.002,0.0007  # 15,10,5,3,1 minutes
CLEANUP_JOB_CRON=*/5 * * * *  # Every 5 minutes
```

**Note**: Values less than 1 represent fractional days (e.g., 0.0104 days ≈ 15 minutes)

## Security Considerations

- **Email Content**: Warning and deletion emails do not contain sensitive data beyond workspace metadata
- **Authentication**: Accessing workspace via email link requires authentication
- **Authorization**: Only workspace owners receive notifications
- **Data Deletion**: All data is permanently deleted (hard-delete, no recovery)
- **No Audit Logs**: Deletion events are not logged (as per requirements)

## Future Enhancements

Potential improvements for future versions:

- Soft-delete with recovery period
- User-configurable retention preferences
- Deletion audit logs for compliance
- Workspace export before deletion
- Batch notification emails (digest mode)
- Manual cleanup triggers via admin API
- Workspace usage metrics dashboard

## References

- Source Code:

  - `backend/app/core/scheduler.py` - Background job scheduler
  - `backend/app/services/workspace_cleanup_service.py` - Cleanup logic
  - `backend/app/services/email_service.py` - Email templates
  - `backend/app/core/config.py` - Configuration settings
  - `backend/app/main.py` - Lifecycle integration

- Tests:

  - `backend/app/tests/test_workspace_cleanup_service.py` - Unit tests

- Documentation:
  - `backend/.env.example` - Configuration examples
  - `docs/03-data-model-design.md` - Workspace data model
