# Workspace API Implementation

This implementation provides comprehensive workspace creation and management APIs for the Deita platform, including GDPR compliance, automatic cleanup, and security features.

## 📁 File Structure

```
backend/app/
├── api/
│   ├── workspace.py     # Core workspace API endpoints
│   ├── admin.py         # Admin & GDPR compliance endpoints
│   └── health.py        # Health check endpoints
├── models/
│   ├── workspace.py     # Database models (Workspace, WorkspaceUsage, WorkspaceAuditLog)
│   └── __init__.py      # Updated User model with UUID support
├── schemas/
│   ├── workspace.py     # Pydantic schemas for API validation
│   └── __init__.py      # Schema exports
├── services/
│   ├── workspace.py     # Core workspace business logic
│   ├── auth.py          # Authentication and session management
│   ├── audit.py         # GDPR compliance and audit logging
│   └── background_jobs.py # Background job processing
├── tests/
│   └── test_workspace.py # Comprehensive test suite
└── main.py              # Updated FastAPI app with new routes
```

## 🚀 API Endpoints

### Core Workspace Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/v1/workspaces` | Create owned workspace (requires auth) |
| `POST` | `/v1/workspaces/orphan` | Create orphan workspace (anonymous) |
| `GET` | `/v1/workspaces` | List workspaces with pagination & filtering |
| `GET` | `/v1/workspaces/{id}` | Get workspace details |
| `PUT` | `/v1/workspaces/{id}` | Update workspace metadata |
| `DELETE` | `/v1/workspaces/{id}` | Delete workspace |
| `POST` | `/v1/workspaces/{id}/claim` | Claim orphan workspace |

### Workspace Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `PUT` | `/v1/workspaces/{id}/visibility` | Change visibility settings |
| `POST` | `/v1/workspaces/{id}/share` | Generate sharing links |
| `GET` | `/v1/workspaces/{id}/usage` | Get storage & usage stats |
| `POST` | `/v1/workspaces/{id}/archive` | Archive workspace |
| `GET` | `/v1/workspaces/templates` | List workspace templates |
| `POST` | `/v1/workspaces/validate-name` | Validate name availability |

### GDPR Compliance

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/admin/users/{id}/data-export` | Export user data (Right to Access) |
| `DELETE` | `/v1/admin/users/{id}/data` | Delete user data (Right to Erasure) |
| `PUT` | `/v1/admin/users/{id}/data-correction` | Correct user data (Right to Rectification) |
| `PUT` | `/v1/admin/users/{id}/data-processing/restrict` | Restrict processing |

### Admin & Background Jobs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/admin/background-jobs` | List all background jobs |
| `POST` | `/v1/admin/background-jobs/orphan-cleanup` | Trigger orphan cleanup |
| `GET` | `/v1/admin/system-health` | System health status |
| `GET` | `/v1/admin/workspace-statistics` | Workspace usage statistics |

## 🗃️ Database Schema

### Core Tables

- **`workspaces`** - Main workspace table with UUID keys
- **`workspace_usage`** - Usage tracking (storage, files, queries)
- **`workspace_audit_logs`** - GDPR-compliant audit trail
- **`users`** - Updated with UUID support for scalability

### Key Features

- **UUID Primary Keys** - Better scalability and security
- **Proper Indexing** - Optimized for common query patterns
- **Cascade Deletion** - Automatic cleanup of related data
- **Audit Logging** - Complete trail for GDPR compliance
- **Storage Quotas** - 50MB for orphan, 200MB for owned workspaces

## 🔐 Security & GDPR

### Authentication & Authorization
- Session-based access for anonymous users
- Owner-based access control for workspaces
- Public/private visibility settings
- Secure UUID generation for workspace IDs

### GDPR Compliance
- **Right to Access** - Complete data export functionality
- **Right to Erasure** - Comprehensive data deletion
- **Right to Rectification** - Data correction mechanisms
- **Audit Trail** - All operations logged with IP/User-Agent
- **Data Retention** - Automatic cleanup based on retention policies

### Automatic Cleanup
- **Orphan Workspaces** - 30 days expiration
- **Inactive Workspaces** - 60 days for owned workspaces
- **Audit Logs** - 7 years retention for compliance
- **Background Jobs** - Automated maintenance tasks

## 🧪 Testing

Comprehensive test suite covering:
- API endpoint functionality
- Business logic validation  
- Data integrity checks
- Edge cases and error handling
- GDPR compliance workflows

## 📊 Usage Examples

### Create Orphan Workspace (Anonymous User)
```bash
curl -X POST /v1/workspaces/orphan \
  -H "Content-Type: application/json" \
  -d '{"name": "My Analysis", "description": "Data exploration"}'
```

### List Workspaces with Filtering
```bash
curl "/v1/workspaces?search=analytics&is_public=true&page=1&size=10"
```

### Get Workspace Usage
```bash
curl "/v1/workspaces/{workspace-id}/usage"
```

## 🔧 Configuration

Key configuration options in `app/core/config.py`:

- `MAX_WORKSPACE_STORAGE` - Storage limits
- `DATABASE_URL` - PostgreSQL connection
- `SECRET_KEY` - Encryption key for sessions
- Various retention policies and cleanup intervals

## 🚦 Status & Health

The implementation includes comprehensive health monitoring:
- Database connectivity checks
- Background job status monitoring  
- Storage usage tracking
- System performance metrics

## 🔄 Background Jobs

Automated maintenance includes:
- Daily orphan workspace cleanup
- Weekly inactive workspace cleanup  
- Daily expiration warnings
- Monthly audit log cleanup
- Configurable retry policies with exponential backoff

This implementation provides a solid foundation for workspace management with enterprise-grade security, compliance, and scalability features.