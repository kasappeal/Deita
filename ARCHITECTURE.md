# Save Queries Feature - Architecture

## Component Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend                                  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ PaginatedQueryResult.tsx (Save button)                   │   │
│  │  - handleSaveQuery() → workspaceApi.saveQuery()          │   │
│  └────────────────────────┬─────────────────────────────────┘   │
│                           │                                       │
│  ┌────────────────────────▼─────────────────────────────────┐   │
│  │ api.ts (services)                                         │   │
│  │  - saveQuery(workspaceId, name, query)                    │   │
│  │  - listSavedQueries(workspaceId)                          │   │
│  │  - SavedQuery interface                                   │   │
│  └────────────────────────┬─────────────────────────────────┘   │
└─────────────────────────────┼─────────────────────────────────────┘
                              │
                    HTTP POST/GET
                              │
┌─────────────────────────────┼─────────────────────────────────────┐
│                         Backend                                    │
│                             │                                      │
│  ┌──────────────────────────▼─────────────────────────────────┐  │
│  │ workspaces.py (API Endpoints)                              │  │
│  │  - POST /workspaces/{id}/queries → save_query()            │  │
│  │  - GET  /workspaces/{id}/queries → list_saved_queries()    │  │
│  └────────────────────────┬───────────────────────────────────┘  │
│                           │                                       │
│  ┌────────────────────────▼───────────────────────────────────┐  │
│  │ workspace_service.py (Business Logic)                      │  │
│  │  - save_query()                                            │  │
│  │    • Validate permissions                                  │  │
│  │    • Check duplicate names                                 │  │
│  │    • Create SavedQuery record                              │  │
│  │  - list_saved_queries()                                    │  │
│  │    • Validate permissions                                  │  │
│  │    • Return queries ordered by created_at DESC             │  │
│  └────────────────────────┬───────────────────────────────────┘  │
│                           │                                       │
│  ┌────────────────────────▼───────────────────────────────────┐  │
│  │ saved_query.py (Model)                                     │  │
│  │  - id: UUID                                                │  │
│  │  - workspace_id: UUID (FK → workspaces, CASCADE)           │  │
│  │  - name: String                                            │  │
│  │  - query: Text                                             │  │
│  │  - created_at: DateTime                                    │  │
│  └────────────────────────┬───────────────────────────────────┘  │
│                           │                                       │
└─────────────────────────────┼─────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │ saved_queries   │
                    │      table      │
                    └─────────────────┘
```

## Data Flow: Save Query

1. **User clicks "Save" button** in PaginatedQueryResult component
2. **Prompt dialog** asks for query name
3. **Frontend** calls `workspaceApi.saveQuery(workspaceId, name, query)`
4. **Backend endpoint** `POST /workspaces/{id}/queries` receives request
5. **WorkspaceService.save_query()** validates:
   - Workspace exists
   - User has permission (public workspace or owner of private)
   - Query name is unique within workspace
6. **Create SavedQuery** record in database
7. **Return response** with saved query details (id, name, query, created_at)
8. **Show success toast** notification to user

## Data Flow: List Queries

1. **Component** calls `workspaceApi.listSavedQueries(workspaceId)`
2. **Backend endpoint** `GET /workspaces/{id}/queries` receives request
3. **WorkspaceService.list_saved_queries()** validates:
   - Workspace exists
   - User has permission to access workspace
4. **Query database** for all saved queries in workspace
5. **Return list** ordered by created_at DESC
6. **Display queries** in frontend component

## Permission Model

| Workspace Type | Anonymous User | Workspace Owner | Other Users |
|----------------|----------------|-----------------|-------------|
| Public         | ✅ Save/List   | ✅ Save/List    | ✅ Save/List |
| Private        | ❌ Denied      | ✅ Save/List    | ❌ Denied   |
| Orphan         | ✅ Save/List   | N/A             | ✅ Save/List |

## Database Schema

```sql
CREATE TABLE saved_queries (
    id UUID PRIMARY KEY,
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    query TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX ix_saved_queries_id ON saved_queries(id);
CREATE INDEX ix_saved_queries_workspace_id ON saved_queries(workspace_id);
```

## API Endpoints

### Save Query
```
POST /v1/workspaces/{workspace_id}/queries
Content-Type: application/json

Request Body:
{
  "name": "Query Name",
  "query": "SELECT * FROM table"
}

Response (201):
{
  "id": "uuid",
  "name": "Query Name",
  "query": "SELECT * FROM table",
  "created_at": "2025-10-03T10:00:00Z"
}
```

### List Queries
```
GET /v1/workspaces/{workspace_id}/queries

Response (200):
[
  {
    "id": "uuid",
    "name": "Query Name",
    "query": "SELECT * FROM table",
    "created_at": "2025-10-03T10:00:00Z"
  }
]
```

## Files Changed

### Backend
- `app/models/saved_query.py` - New SavedQuery model
- `app/schemas/saved_query.py` - New Pydantic schemas
- `app/services/workspace_service.py` - Added save_query() and list_saved_queries()
- `app/api/workspaces.py` - Added two new endpoints
- `app/models/__init__.py` - Export SavedQuery
- `app/schemas/__init__.py` - Export SavedQuery schemas
- `migrations/versions/004_add_saved_queries.py` - Database migration
- `app/tests/test_saved_queries_endpoints.py` - Comprehensive tests

### Frontend
- `src/services/api.ts` - Added SavedQuery interface and listSavedQueries()

## Test Coverage

✅ Save query in public workspace (anonymous)
✅ Save query in private workspace (owner)
✅ Deny save in private workspace (non-owner)
✅ Duplicate name validation
✅ Invalid input validation (422)
✅ Nonexistent workspace (404)
✅ List queries with proper permissions
✅ Empty workspace handling
