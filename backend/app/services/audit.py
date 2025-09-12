"""
GDPR compliance utilities and audit logging.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from uuid import UUID
from enum import Enum


class DataProcessingPurpose(Enum):
    """Enumeration of data processing purposes for GDPR compliance."""
    WORKSPACE_MANAGEMENT = "workspace_management"
    USER_AUTHENTICATION = "user_authentication"
    ANALYTICS = "analytics"
    SECURITY_MONITORING = "security_monitoring"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"


class GDPRCompliance:
    """GDPR compliance utilities and data protection methods."""
    
    def __init__(self):
        self.retention_policies = {
            "workspace_data": timedelta(days=365 * 2),  # 2 years
            "audit_logs": timedelta(days=365 * 7),      # 7 years for legal compliance
            "orphan_workspaces": timedelta(days=30),     # 30 days
            "user_sessions": timedelta(days=1),          # 1 day for anonymous sessions
        }
    
    def check_data_retention(self, data_type: str, created_at: datetime) -> bool:
        """Check if data should be retained based on GDPR policies."""
        if data_type not in self.retention_policies:
            return True  # Conservative approach - retain if no policy defined
        
        retention_period = self.retention_policies[data_type]
        expiry_date = created_at + retention_period
        return datetime.utcnow() < expiry_date
    
    def generate_data_export(self, user_id: UUID, workspace_data: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive data export for user (Right to Access)."""
        export_data = {
            "export_metadata": {
                "user_id": str(user_id),
                "generated_at": datetime.utcnow().isoformat(),
                "export_version": "1.0",
                "data_controller": "Deita Platform",
            },
            "workspace_data": {
                "workspaces": workspace_data,
                "total_workspaces": len(workspace_data),
            },
            "processing_activities": self._get_processing_activities(user_id),
            "data_retention_info": self._get_retention_info(),
        }
        return export_data
    
    def anonymize_workspace_data(self, workspace_data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize workspace data while preserving functionality."""
        anonymized = workspace_data.copy()
        
        # Remove or anonymize personally identifiable information
        if "owner_id" in anonymized:
            anonymized["owner_id"] = None
        
        if "audit_logs" in anonymized:
            for log in anonymized["audit_logs"]:
                if "user_id" in log:
                    log["user_id"] = None
                if "ip_address" in log:
                    log["ip_address"] = self._anonymize_ip(log["ip_address"])
        
        return anonymized
    
    def validate_consent(self, user_id: UUID, purpose: DataProcessingPurpose) -> bool:
        """Validate user consent for specific data processing purpose."""
        # In a real implementation, this would check a consent database
        # For now, return True as a placeholder
        return True
    
    def log_consent_change(self, user_id: UUID, purpose: DataProcessingPurpose, granted: bool):
        """Log consent changes for audit trail."""
        # In a real implementation, this would log to a consent audit system
        pass
    
    def _get_processing_activities(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Get data processing activities for the user."""
        return [
            {
                "purpose": "Workspace Management",
                "legal_basis": "Legitimate Interest",
                "data_categories": ["workspace_metadata", "usage_statistics"],
                "retention_period": "2 years",
            },
            {
                "purpose": "Security Monitoring",
                "legal_basis": "Legitimate Interest",
                "data_categories": ["access_logs", "ip_addresses"],
                "retention_period": "1 year",
            }
        ]
    
    def _get_retention_info(self) -> Dict[str, str]:
        """Get data retention information."""
        return {
            "workspace_data": "2 years from last access",
            "audit_logs": "7 years for legal compliance",
            "orphan_workspaces": "30 days from creation",
            "user_sessions": "1 day for anonymous users",
        }
    
    def _anonymize_ip(self, ip_address: str) -> str:
        """Anonymize IP address by masking last octet."""
        if not ip_address:
            return ""
        
        # Simple IPv4 anonymization
        if "." in ip_address:
            parts = ip_address.split(".")
            if len(parts) == 4:
                return f"{parts[0]}.{parts[1]}.{parts[2]}.xxx"
        
        return "anonymized"


class AuditLogger:
    """Audit logging system for GDPR compliance and security monitoring."""
    
    def __init__(self):
        self.gdpr_compliance = GDPRCompliance()
    
    async def log_workspace_access(
        self,
        workspace_id: UUID,
        user_id: Optional[UUID],
        action: str,
        ip_address: Optional[str],
        user_agent: Optional[str],
        additional_data: Optional[Dict[str, Any]] = None
    ):
        """Log workspace access for audit trail."""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "workspace_id": str(workspace_id),
            "user_id": str(user_id) if user_id else None,
            "action": action,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "additional_data": additional_data or {},
        }
        
        # In a real implementation, this would be stored in the database
        # For now, we'll just validate the structure
        return audit_entry
    
    async def log_data_processing(
        self,
        user_id: Optional[UUID],
        purpose: DataProcessingPurpose,
        data_types: List[str],
        action: str,
        ip_address: Optional[str] = None
    ):
        """Log data processing activities for GDPR compliance."""
        processing_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": str(user_id) if user_id else None,
            "purpose": purpose.value,
            "data_types": data_types,
            "action": action,
            "ip_address": ip_address,
            "legal_basis": "legitimate_interest",  # Would be determined based on purpose
        }
        
        return processing_log
    
    async def log_gdpr_request(
        self,
        user_id: UUID,
        request_type: str,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log GDPR data subject requests (access, rectification, erasure, etc.)."""
        gdpr_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": str(user_id),
            "request_type": request_type,
            "status": status,
            "details": details or {},
            "processed_by": "system",  # Would include admin user in real implementation
        }
        
        return gdpr_log


# Global instances
gdpr_compliance = GDPRCompliance()
audit_logger = AuditLogger()