# Save Queries Feature Implementation

## Summary

This implementation adds the ability to save and list SQL queries in workspaces. It follows the existing architecture patterns and integrates seamlessly with the workspace permission system.

## Backend Changes

### 1. Database Model (`backend/app/models/saved_query.py`)
- Created `SavedQuery` model with the following fields:
  - `id`: UUID primary key
  - `workspace_id`: Foreign key to workspaces table with CASCADE delete
  - `name`: Query name (string)
  - `query`: SQL query text (text field)
  - `created_at`: Timestamp

### 2. Database Migration (`backend/migrations/versions/004_add_saved_queries.py`)
- Creates `saved_queries` table
- Adds indexes on `id` and `workspace_id`
- Ensures CASCADE delete when workspace is deleted

### 3. Pydantic Schemas (`backend/app/schemas/saved_query.py`)
- `SaveQueryCreate`: Input schema for creating queries (name, query)
- `SavedQuery`: Response schema with all fields including id and created_at

### 4. Service Layer (`backend/app/services/workspace_service.py`)
- `save_query()`: Validates permissions, checks for duplicate names, creates query record
- `list_saved_queries()`: Returns all saved queries for a workspace, ordered by creation date (descending)

### 5. API Endpoints (`backend/app/api/workspaces.py`)
- `POST /v1/workspaces/{workspace_id}/queries`: Save a new query
- `GET /v1/workspaces/{workspace_id}/queries`: List all saved queries

### 6. Tests (`backend/app/tests/test_saved_queries_endpoints.py`)
Comprehensive test coverage including:
- Saving queries in public workspaces (anonymous users)
- Saving queries in private workspaces (authenticated users only)
- Authorization checks (403 for unauthorized access)
- Duplicate name validation (400 for duplicate names)
- Invalid input validation (422 for missing fields)
- Listing queries with proper permissions
- Empty workspace handling

## Frontend Changes

### API Client (`frontend/src/services/api.ts`)
- Added `SavedQuery` TypeScript interface
- Updated `saveQuery()` return type to use `SavedQuery` interface
- Added `listSavedQueries()` method to fetch all saved queries

## Permission Model

The implementation follows the existing workspace permission model:

- **Public Workspaces**: Anyone with the URL can save and list queries
- **Private Workspaces**: Only the workspace owner can save and list queries
- **Orphan Workspaces**: Treated as public for query operations

## Key Features

✅ Save queries with custom names
✅ Duplicate name prevention within workspace
✅ Cascade deletion when workspace is deleted
✅ List queries ordered by creation date (newest first)
✅ Full permission checks (public/private workspace handling)
✅ Comprehensive error handling
✅ Test coverage for all scenarios

## What's NOT Included (Future Enhancements)

The following features from the issue requirements can be added incrementally:

- Query parameter storage
- Query metadata (execution time, result count, referenced tables)
- Tagging and categorization
- Folder/category organization
- Query modification tracking
- Performance metrics tracking
- Search and filtering
- Pagination for large collections
- Query validation before saving
- Update/rename saved queries
- Delete saved queries
- Query sharing
- Export query collections

## API Examples

### Save a Query
```bash
POST /v1/workspaces/{workspace_id}/queries
Content-Type: application/json

{
  "name": "Top Customers",
  "query": "SELECT * FROM customers ORDER BY total DESC LIMIT 10"
}

Response (201):
{
  "id": "uuid-here",
  "name": "Top Customers",
  "query": "SELECT * FROM customers ORDER BY total DESC LIMIT 10",
  "created_at": "2025-10-03T10:00:00Z"
}
```

### List Saved Queries
```bash
GET /v1/workspaces/{workspace_id}/queries

Response (200):
[
  {
    "id": "uuid-here",
    "name": "Top Customers",
    "query": "SELECT * FROM customers ORDER BY total DESC LIMIT 10",
    "created_at": "2025-10-03T10:00:00Z"
  }
]
```

## Database Schema

```sql
CREATE TABLE saved_queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    query TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX ix_saved_queries_id ON saved_queries(id);
CREATE INDEX ix_saved_queries_workspace_id ON saved_queries(workspace_id);
```

## Testing

Run backend tests:
```bash
cd backend
uv run pytest app/tests/test_saved_queries_endpoints.py -v
```

Run all tests:
```bash
make test-be
```

## Migration

To apply the database migration:
```bash
cd backend
uv run alembic upgrade head
```
