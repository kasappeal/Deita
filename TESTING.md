# Testing Guide for Save Queries Feature

## Prerequisites

1. **Start the backend server:**
   ```bash
   cd backend
   uv run alembic upgrade head  # Apply database migrations
   uv fastapi dev --host=0.0.0.0 --port=8000
   ```

2. **Create a test workspace** (if you don't have one):
   ```bash
   curl -X POST http://localhost:8000/v1/workspaces/ \
     -H "Content-Type: application/json" \
     -d '{"name": "Test Workspace"}'
   ```
   
   Note the `id` from the response for use in subsequent requests.

## Manual Testing

### 1. Save a Query

```bash
# Save a query to a workspace
curl -X POST http://localhost:8000/v1/workspaces/{workspace_id}/queries \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sample Query",
    "query": "SELECT * FROM customers LIMIT 10"
  }'
```

**Expected Response (201):**
```json
{
  "id": "uuid-here",
  "name": "Sample Query",
  "query": "SELECT * FROM customers LIMIT 10",
  "created_at": "2025-10-03T10:00:00Z"
}
```

### 2. List Saved Queries

```bash
# List all saved queries in a workspace
curl -X GET http://localhost:8000/v1/workspaces/{workspace_id}/queries
```

**Expected Response (200):**
```json
[
  {
    "id": "uuid-here",
    "name": "Sample Query",
    "query": "SELECT * FROM customers LIMIT 10",
    "created_at": "2025-10-03T10:00:00Z"
  }
]
```

### 3. Test Duplicate Name (Should Fail)

```bash
# Try to save another query with the same name
curl -X POST http://localhost:8000/v1/workspaces/{workspace_id}/queries \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sample Query",
    "query": "SELECT * FROM products"
  }'
```

**Expected Response (400):**
```json
{
  "error": "Query with name 'Sample Query' already exists in this workspace"
}
```

### 4. Test Invalid Input (Should Fail)

```bash
# Try to save a query without a name
curl -X POST http://localhost:8000/v1/workspaces/{workspace_id}/queries \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT * FROM test"
  }'
```

**Expected Response (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Automated Testing

### Run Backend Tests

```bash
cd backend
uv run pytest app/tests/test_saved_queries_endpoints.py -v
```

**Expected Output:**
```
test_saved_queries_endpoints.py::TestSaveQuery::test_save_query_in_public_workspace_without_auth PASSED
test_saved_queries_endpoints.py::TestSaveQuery::test_save_query_in_private_workspace_with_auth PASSED
test_saved_queries_endpoints.py::TestSaveQuery::test_save_query_in_private_workspace_without_auth PASSED
test_saved_queries_endpoints.py::TestSaveQuery::test_save_duplicate_query_name PASSED
test_saved_queries_endpoints.py::TestSaveQuery::test_save_query_with_invalid_data PASSED
test_saved_queries_endpoints.py::TestSaveQuery::test_save_query_in_nonexistent_workspace PASSED
test_saved_queries_endpoints.py::TestListSavedQueries::test_list_queries_in_public_workspace PASSED
test_saved_queries_endpoints.py::TestListSavedQueries::test_list_queries_in_private_workspace_with_auth PASSED
test_saved_queries_endpoints.py::TestListSavedQueries::test_list_queries_in_private_workspace_without_auth PASSED
test_saved_queries_endpoints.py::TestListSavedQueries::test_list_queries_empty_workspace PASSED
test_saved_queries_endpoints.py::TestListSavedQueries::test_list_queries_in_nonexistent_workspace PASSED

============ 11 passed in X.XXs ============
```

### Run All Backend Tests

```bash
cd backend
uv run pytest -v
```

## Frontend Testing

### 1. Start Frontend Development Server

```bash
cd frontend
npm run dev
```

### 2. Test Save Query in UI

1. Navigate to a workspace
2. Execute a query (or view a table)
3. Click the "Save" button
4. Enter a query name in the prompt
5. Verify success toast appears
6. Check that query was saved by calling the API

### 3. Test List Queries (Future UI Component)

Once a UI component is added to display saved queries:
1. Navigate to saved queries section
2. Verify queries are displayed
3. Verify they're ordered by creation date (newest first)

## API Documentation

Once the server is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/v1/openapi.json

Navigate to the "Workspaces" section to see the new endpoints.

## Database Verification

### Check Saved Queries in Database

```bash
# Connect to PostgreSQL
psql -h localhost -U deita_user -d deita_db

# Query saved queries
SELECT id, workspace_id, name, query, created_at 
FROM saved_queries 
ORDER BY created_at DESC;
```

### Check Migration Status

```bash
cd backend
uv run alembic current
```

**Expected Output:**
```
004_add_saved_queries (head)
```

## Common Issues

### Migration Not Applied
**Problem:** Tables don't exist in database

**Solution:**
```bash
cd backend
uv run alembic upgrade head
```

### Import Errors
**Problem:** Module not found errors

**Solution:**
```bash
cd backend
uv sync  # Install/update dependencies
```

### Port Already in Use
**Problem:** Port 8000 is already in use

**Solution:**
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
uv fastapi dev --host=0.0.0.0 --port=8001
```

## Next Steps

After verifying the basic functionality:

1. **Create UI Components** to display and manage saved queries
2. **Add Update/Delete Endpoints** for query management
3. **Implement Search/Filter** for large query collections
4. **Add Query Metadata** (execution time, referenced tables, etc.)
5. **Create Tagging System** for better organization
