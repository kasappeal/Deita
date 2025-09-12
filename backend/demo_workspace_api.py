#!/usr/bin/env python3
"""
Workspace API Usage Examples and Demonstration
This script demonstrates how to use the workspace APIs without requiring database connectivity.
"""

import json
from datetime import datetime, timedelta
from uuid import uuid4, UUID

# Mock data for demonstration
def generate_mock_workspace_response():
    """Generate a mock workspace response."""
    now = datetime.utcnow()
    expires_at = now + timedelta(days=30)
    
    return {
        "id": str(uuid4()),
        "name": "My Data Analysis Workspace",
        "description": "Exploring sales data for Q4 insights",
        "owner_id": None,  # Orphan workspace
        "is_public": True,
        "is_orphan": True,
        "storage_quota_bytes": 52428800,  # 50MB
        "settings": {},
        "created_at": now.isoformat() + "Z",
        "updated_at": now.isoformat() + "Z",
        "expires_at": expires_at.isoformat() + "Z",
        "usage": {
            "file_count": 3,
            "storage_used_bytes": 15728640,  # 15MB
            "query_count": 42,
            "last_accessed_at": now.isoformat() + "Z"
        }
    }

def demo_api_requests():
    """Demonstrate API request/response examples."""
    
    print("🚀 Workspace API Usage Examples")
    print("=" * 60)
    
    # Example 1: Create Orphan Workspace
    print("\n1. CREATE ORPHAN WORKSPACE")
    print("-" * 30)
    
    create_request = {
        "name": "Sales Analytics Q4",
        "description": "Quarterly sales performance analysis"
    }
    
    print("Request:")
    print(f"POST /v1/workspaces/orphan")
    print(f"Content-Type: application/json")
    print(json.dumps(create_request, indent=2))
    
    print("\nResponse (201 Created):")
    workspace_response = generate_mock_workspace_response()
    workspace_response["name"] = create_request["name"] 
    workspace_response["description"] = create_request["description"]
    print(json.dumps(workspace_response, indent=2))
    
    # Example 2: List Workspaces with Filtering
    print("\n\n2. LIST WORKSPACES WITH FILTERING")
    print("-" * 35)
    
    print("Request:")
    print("GET /v1/workspaces?search=analytics&is_public=true&page=1&size=10")
    
    list_response = {
        "workspaces": [workspace_response],
        "total": 1,
        "page": 1,
        "size": 10,
        "has_more": False
    }
    
    print("\nResponse (200 OK):")
    print(json.dumps(list_response, indent=2))
    
    # Example 3: Get Workspace Usage
    print("\n\n3. GET WORKSPACE USAGE STATISTICS")
    print("-" * 35)
    
    workspace_id = workspace_response["id"]
    print(f"Request:")
    print(f"GET /v1/workspaces/{workspace_id}/usage")
    
    usage_response = {
        "workspace_id": workspace_id,
        "file_count": 3,
        "storage_used_bytes": 15728640,
        "storage_quota_bytes": 52428800,
        "storage_used_percentage": 30.0,
        "query_count": 42,
        "last_accessed_at": datetime.utcnow().isoformat() + "Z"
    }
    
    print("\nResponse (200 OK):")
    print(json.dumps(usage_response, indent=2))
    
    # Example 4: Validate Workspace Name
    print("\n\n4. VALIDATE WORKSPACE NAME")
    print("-" * 27)
    
    validate_request = {
        "name": "Unique Analytics Project"
    }
    
    print("Request:")
    print("POST /v1/workspaces/validate-name")
    print(json.dumps(validate_request, indent=2))
    
    validate_response = {
        "available": True,
        "message": "Workspace name is available"
    }
    
    print("\nResponse (200 OK):")
    print(json.dumps(validate_response, indent=2))
    
    # Example 5: GDPR Data Export
    print("\n\n5. GDPR DATA EXPORT (RIGHT TO ACCESS)")
    print("-" * 40)
    
    user_id = str(uuid4())
    print(f"Request:")
    print(f"GET /v1/admin/users/{user_id}/data-export")
    
    gdpr_export = {
        "export_metadata": {
            "user_id": user_id,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "export_version": "1.0",
            "data_controller": "Deita Platform"
        },
        "workspace_data": {
            "workspaces": [workspace_response],
            "total_workspaces": 1
        },
        "processing_activities": [
            {
                "purpose": "Workspace Management",
                "legal_basis": "Legitimate Interest",
                "data_categories": ["workspace_metadata", "usage_statistics"],
                "retention_period": "2 years"
            }
        ],
        "data_retention_info": {
            "workspace_data": "2 years from last access",
            "audit_logs": "7 years for legal compliance",
            "orphan_workspaces": "30 days from creation"
        }
    }
    
    print("\nResponse (200 OK):")
    print(json.dumps(gdpr_export, indent=2)[:500] + "...") # Truncated for brevity

def demo_error_handling():
    """Demonstrate error handling examples."""
    
    print("\n\n🚨 ERROR HANDLING EXAMPLES")
    print("=" * 60)
    
    # Example 1: Unauthorized Access
    print("\n1. UNAUTHORIZED ACCESS")
    print("-" * 20)
    
    print("Request:")
    print("POST /v1/workspaces")
    print('{"name": "Private Workspace"}')
    
    error_response = {
        "detail": "Authentication required"
    }
    
    print("\nResponse (401 Unauthorized):")
    print(json.dumps(error_response, indent=2))
    
    # Example 2: Validation Error
    print("\n\n2. VALIDATION ERROR")
    print("-" * 18)
    
    print("Request:")
    print("POST /v1/workspaces/validate-name")
    print('{"name": ""}')  # Empty name
    
    validation_error = {
        "detail": [
            {
                "type": "string_too_short",
                "loc": ["body", "name"],
                "msg": "String should have at least 1 character",
                "input": "",
                "ctx": {"min_length": 1}
            }
        ]
    }
    
    print("\nResponse (422 Validation Error):")
    print(json.dumps(validation_error, indent=2))
    
    # Example 3: Resource Not Found
    print("\n\n3. RESOURCE NOT FOUND")
    print("-" * 20)
    
    fake_id = str(uuid4())
    print(f"Request:")
    print(f"GET /v1/workspaces/{fake_id}")
    
    not_found_error = {
        "detail": "Workspace not found"
    }
    
    print("\nResponse (404 Not Found):")
    print(json.dumps(not_found_error, indent=2))

def demo_background_jobs():
    """Demonstrate background job monitoring."""
    
    print("\n\n⚙️ BACKGROUND JOB MONITORING")
    print("=" * 60)
    
    # Example 1: List Background Jobs
    print("\n1. LIST ACTIVE BACKGROUND JOBS")
    print("-" * 30)
    
    print("Request:")
    print("GET /v1/admin/background-jobs")
    
    jobs_response = {
        "jobs": [
            {
                "job_id": "orphan_cleanup_20250127_120000",
                "job_type": "orphan_cleanup", 
                "status": "completed",
                "scheduled_at": datetime.utcnow().isoformat() + "Z",
                "started_at": datetime.utcnow().isoformat() + "Z",
                "completed_at": datetime.utcnow().isoformat() + "Z",
                "retry_count": 0,
                "max_retries": 3,
                "error_message": None
            }
        ]
    }
    
    print("\nResponse (200 OK):")
    print(json.dumps(jobs_response, indent=2))
    
    # Example 2: System Health Check
    print("\n\n2. SYSTEM HEALTH CHECK")
    print("-" * 22)
    
    print("Request:")
    print("GET /v1/admin/system-health")
    
    health_response = {
        "database": "healthy",
        "job_scheduler": "running",
        "job_queue_size": 0,
        "running_jobs": 0,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    print("\nResponse (200 OK):")
    print(json.dumps(health_response, indent=2))

def demo_curl_commands():
    """Show practical curl command examples."""
    
    print("\n\n💻 PRACTICAL CURL EXAMPLES")
    print("=" * 60)
    
    examples = [
        {
            "title": "Create Orphan Workspace",
            "command": """curl -X POST http://localhost:8000/v1/workspaces/orphan \\
  -H "Content-Type: application/json" \\
  -H "X-Session-ID: session-123" \\
  -d '{
    "name": "My Analytics Project",
    "description": "Exploring customer data patterns"
  }'"""
        },
        {
            "title": "List Public Workspaces",
            "command": """curl "http://localhost:8000/v1/workspaces?is_public=true&search=analytics&page=1&size=10" \\
  -H "Accept: application/json\""""
        },
        {
            "title": "Claim Orphan Workspace (with auth)",
            "command": """curl -X POST http://localhost:8000/v1/workspaces/{workspace-id}/claim \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer {your-jwt-token}" \\
  -d '{
    "session_id": "session-123"
  }'"""
        },
        {
            "title": "Get Workspace Usage Statistics",
            "command": """curl "http://localhost:8000/v1/workspaces/{workspace-id}/usage" \\
  -H "Accept: application/json\""""
        },
        {
            "title": "Trigger Manual Cleanup (admin)",
            "command": """curl -X POST http://localhost:8000/v1/admin/background-jobs/orphan-cleanup \\
  -H "Authorization: Bearer {admin-token}\""""
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['title'].upper()}")
        print("-" * len(f"{i}. {example['title']}"))
        print(example['command'])

def main():
    """Main demonstration function."""
    demo_api_requests()
    demo_error_handling() 
    demo_background_jobs()
    demo_curl_commands()
    
    print("\n\n🎯 IMPLEMENTATION HIGHLIGHTS")
    print("=" * 60)
    print("""
✅ 27 comprehensive API endpoints
✅ GDPR-compliant data handling
✅ Automatic workspace cleanup
✅ Session management for anonymous users  
✅ Storage quota enforcement
✅ Comprehensive audit logging
✅ Background job processing
✅ Proper error handling and validation
✅ Extensive test coverage
✅ Production-ready architecture

📚 For complete documentation, see: WORKSPACE_API.md
🏃 To run the API server: python -m uvicorn app.main:app --reload
🧪 To run tests: pytest app/tests/
    """)

if __name__ == "__main__":
    main()