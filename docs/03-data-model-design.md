# Data Model Design

## Overview
The data model for Deita is designed to support flexible data exploration, workspace management, and AI-powered analytics. It leverages PostgreSQL for metadata and DuckDB for analytical queries on user-uploaded data.

## Entity Relationship Diagram (MermaidJS)
```mermaid
erDiagram
    USER |o--o{ WORKSPACE : owns
    WORKSPACE ||--o{ FILE : contains
    FILE ||--o{ TABLE : has
    TABLE ||--o{ QUERY : used_in
    WORKSPACE ||--o{ QUERY : saved_in
    WORKSPACE ||--o{ EXPORTFILE : has_export

    USER {
        int id PK
        string email
        datetime created_at "default now"
    }

    WORKSPACE {
        int id PK
        int owner_id FK "null if orphan"
        string visibility "public (default)/private"
        datetime created_at "default now"
        datetime last_accessed_at
    }

    FILE {
        int id PK
        int workspace_id FK
        string filename
        string storage_path
        string file_type "excel/csv"
        string status "pending (default)/processed/error"
        datetime uploaded_at "default now"
    }

    TABLE {
        int id PK
        int workspace_id FK
        int file_id FK
        string slug "unique per workspace"
        string name "unique per workspace"
        jsonb schema_json
        int row_count
    }

    QUERY {
        int id PK
        int workspace_id FK
        string name
        string sql_text
        boolean ai_generated
        datetime created_at "default now"
    }

    EXPORTFILE {
        string id PK "unique token for download URL"
        int workspace_id FK
        string filename
        string format "csv/excel"
        string storage_path
        datetime created_at "default now"
        datetime expires_at
        boolean deleted "true if deleted after expiration"
    }
```

## Key Entities

- **User**: Owns workspaces and queries.
- **Workspace**: Collection of files, tables, and queries. Can be orphan (owner_id null) or owned (owner_id not null).
- **File**: Uploaded Excel/CSV file, linked to a workspace.
- **Table**: Logical table (Excel tab or CSV), linked to a file.
- **Query**: SQL query, can be user-written or AI-generated, linked to workspace.

## DuckDB Usage
- Each workspace's uploaded files are loaded into DuckDB for fast, in-memory analytical queries.
- Table schemas and row counts are stored in PostgreSQL for metadata and quick lookup.

## Relationships & Constraints
- Orphan workspaces have no owner (owner_id is null).
- Only SELECT queries are allowed (enforced at backend).
- File size and workspace limits enforced at upload.
- Automatic deletion of unused workspaces/files per PRD.

## Extensibility
- Model supports future features: query sharing, export history, AI relationship suggestions.
