"""
Workspace API endpoints for creation, management, and operations.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Workspace
from app.schemas.workspace import (
    CreateWorkspaceRequest,
    CreateOrphanWorkspaceRequest,
    UpdateWorkspaceRequest,
    ClaimWorkspaceRequest,
    WorkspaceVisibilityRequest,
    ShareWorkspaceRequest,
    WorkspaceFilters,
    WorkspaceResponse,
    WorkspaceListResponse,
    WorkspaceDetailsResponse,
    ValidateWorkspaceNameRequest,
    ValidateWorkspaceNameResponse,
    ShareLinkResponse,
    WorkspaceUsageResponse,
)
from app.services.workspace import WorkspaceService, WorkspaceCleanupService

router = APIRouter()


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host


def get_user_agent(request: Request) -> str:
    """Extract user agent from request."""
    return request.headers.get("User-Agent", "")


# For now, we'll use a simple mock authentication
# In a real implementation, this would be proper JWT/session auth
def get_current_user_id() -> Optional[UUID]:
    """Mock function to get current user ID. Replace with real auth."""
    return None


def get_session_id(request: Request) -> str:
    """Extract or generate session ID for anonymous users."""
    # In a real implementation, this would use cookies or session management
    return request.headers.get("X-Session-ID", "anonymous-session")


@router.post("/workspaces", response_model=WorkspaceResponse, status_code=201)
async def create_workspace(
    data: CreateWorkspaceRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: Optional[UUID] = Depends(get_current_user_id),
):
    """Create a new owned workspace for registered users."""
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = WorkspaceService(db)
    try:
        workspace = await service.create_workspace(
            user_id=current_user_id,
            data=data,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
        )
        return WorkspaceResponse.model_validate(workspace)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/workspaces/orphan", response_model=WorkspaceResponse, status_code=201)
async def create_orphan_workspace(
    data: CreateOrphanWorkspaceRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """Create a new orphan workspace for anonymous users."""
    session_id = get_session_id(request)
    service = WorkspaceService(db)
    
    try:
        workspace = await service.create_orphan_workspace(
            data=data,
            session_id=session_id,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
        )
        return WorkspaceResponse.model_validate(workspace)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/workspaces", response_model=WorkspaceListResponse)
async def list_workspaces(
    db: Session = Depends(get_db),
    current_user_id: Optional[UUID] = Depends(get_current_user_id),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search term"),
    is_public: Optional[bool] = Query(None, description="Filter by visibility"),
    is_orphan: Optional[bool] = Query(None, description="Filter by orphan status"),
    owner_id: Optional[UUID] = Query(None, description="Filter by owner"),
):
    """List workspaces with pagination and filtering."""
    filters = WorkspaceFilters(
        search=search,
        is_public=is_public,
        is_orphan=is_orphan,
        owner_id=owner_id,
    )
    
    service = WorkspaceService(db)
    return await service.list_workspaces(
        user_id=current_user_id,
        filters=filters,
        page=page,
        size=size,
    )


@router.get("/workspaces/{workspace_id}", response_model=WorkspaceDetailsResponse)
async def get_workspace(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user_id: Optional[UUID] = Depends(get_current_user_id),
):
    """Get workspace details and metadata."""
    service = WorkspaceService(db)
    workspace = await service.get_workspace(workspace_id, current_user_id)
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    return WorkspaceDetailsResponse.model_validate(workspace)


@router.put("/workspaces/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: UUID,
    data: UpdateWorkspaceRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: Optional[UUID] = Depends(get_current_user_id),
):
    """Update workspace metadata and settings."""
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = WorkspaceService(db)
    try:
        workspace = await service.update_workspace(
            workspace_id=workspace_id,
            user_id=current_user_id,
            data=data,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
        )
        return WorkspaceResponse.model_validate(workspace)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/workspaces/{workspace_id}", status_code=204)
async def delete_workspace(
    workspace_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: Optional[UUID] = Depends(get_current_user_id),
):
    """Delete workspace and all associated data."""
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = WorkspaceService(db)
    try:
        await service.delete_workspace(
            workspace_id=workspace_id,
            user_id=current_user_id,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/workspaces/{workspace_id}/claim", response_model=WorkspaceResponse)
async def claim_workspace(
    workspace_id: UUID,
    data: ClaimWorkspaceRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: Optional[UUID] = Depends(get_current_user_id),
):
    """Claim orphan workspace for registered users."""
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = WorkspaceService(db)
    try:
        workspace = await service.claim_workspace(
            workspace_id=workspace_id,
            user_id=current_user_id,
            session_id=data.session_id,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
        )
        return WorkspaceResponse.model_validate(workspace)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/workspaces/{workspace_id}/visibility", response_model=WorkspaceResponse)
async def change_workspace_visibility(
    workspace_id: UUID,
    data: WorkspaceVisibilityRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: Optional[UUID] = Depends(get_current_user_id),
):
    """Change workspace visibility settings."""
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # For now, implement this as a simple update
    service = WorkspaceService(db)
    try:
        workspace = await service.update_workspace(
            workspace_id=workspace_id,
            user_id=current_user_id,
            data=UpdateWorkspaceRequest(),
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
        )
        
        # Update visibility
        workspace_obj = db.query(Workspace).filter(Workspace.id == workspace_id).first()
        workspace_obj.is_public = data.is_public
        db.commit()
        db.refresh(workspace_obj)
        
        return WorkspaceResponse.model_validate(workspace_obj)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/workspaces/{workspace_id}/share", response_model=ShareLinkResponse)
async def generate_share_link(
    workspace_id: UUID,
    data: ShareWorkspaceRequest,
    db: Session = Depends(get_db),
    current_user_id: Optional[UUID] = Depends(get_current_user_id),
):
    """Generate and manage sharing links."""
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Verify workspace access
    service = WorkspaceService(db)
    workspace = await service.get_workspace(workspace_id, current_user_id)
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Generate share URL (simplified implementation)
    share_token = "share-" + str(workspace_id)[:8]
    share_url = f"/shared/{share_token}"
    
    expires_at = None
    if data.expires_in_hours:
        from datetime import datetime, timedelta
        expires_at = datetime.utcnow() + timedelta(hours=data.expires_in_hours)
    
    return ShareLinkResponse(
        share_url=share_url,
        expires_at=expires_at,
        allow_edit=data.allow_edit,
    )


@router.get("/workspaces/{workspace_id}/usage", response_model=WorkspaceUsageResponse)
async def get_workspace_usage(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user_id: Optional[UUID] = Depends(get_current_user_id),
):
    """Get workspace storage and resource usage."""
    service = WorkspaceService(db)
    workspace = await service.get_workspace(workspace_id, current_user_id)
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    usage = workspace.usage
    if not usage:
        raise HTTPException(status_code=404, detail="Usage data not found")
    
    storage_used_percentage = (usage.storage_used_bytes / workspace.storage_quota_bytes * 100) if workspace.storage_quota_bytes > 0 else 0
    
    return WorkspaceUsageResponse(
        workspace_id=workspace.id,
        file_count=usage.file_count,
        storage_used_bytes=usage.storage_used_bytes,
        storage_quota_bytes=workspace.storage_quota_bytes,
        storage_used_percentage=storage_used_percentage,
        query_count=usage.query_count,
        last_accessed_at=usage.last_accessed_at,
    )


@router.post("/workspaces/{workspace_id}/archive", response_model=WorkspaceResponse)
async def archive_workspace(
    workspace_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user_id: Optional[UUID] = Depends(get_current_user_id),
):
    """Archive inactive workspaces."""
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # For now, this is a placeholder - archiving would involve moving to cold storage
    service = WorkspaceService(db)
    workspace = await service.get_workspace(workspace_id, current_user_id)
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # In a real implementation, this would:
    # 1. Move files to cold storage
    # 2. Update workspace status to archived
    # 3. Restrict access appropriately
    
    return WorkspaceResponse.model_validate(workspace)


@router.get("/workspaces/templates")
async def list_workspace_templates():
    """List available workspace templates."""
    # Placeholder for workspace templates
    return {
        "templates": [
            {
                "id": "blank",
                "name": "Blank Workspace",
                "description": "Start with an empty workspace",
            },
            {
                "id": "data-analysis", 
                "name": "Data Analysis Template",
                "description": "Pre-configured for data analysis workflows",
            }
        ]
    }


@router.post("/workspaces/validate-name", response_model=ValidateWorkspaceNameResponse)
async def validate_workspace_name(
    data: ValidateWorkspaceNameRequest,
    db: Session = Depends(get_db),
    current_user_id: Optional[UUID] = Depends(get_current_user_id),
):
    """Validate workspace name availability."""
    service = WorkspaceService(db)
    available, message = await service.validate_workspace_name(data.name, current_user_id)
    
    return ValidateWorkspaceNameResponse(
        available=available,
        message=message,
    )