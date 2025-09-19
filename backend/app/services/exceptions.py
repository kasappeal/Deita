"""
Custom exceptions for workspace and file business logic.
"""

class NotFoundException(Exception):
    pass

class ForbiddenException(Exception):
    pass

class BadRequestException(Exception):
    pass


class WorkspaceNotFound(NotFoundException):
    pass

class WorkspaceForbidden(ForbiddenException):
    pass

class WorkspaceQuotaExceeded(BadRequestException):
    pass

class FileTypeNotAllowed(BadRequestException):
    pass

class FileTooLarge(BadRequestException):
    pass

class WorkspaceOrphanModification(BadRequestException):
    pass

class WorkspaceAlreadyClaimed(ForbiddenException):
    pass


class BadQuery(BadRequestException):
    pass

class DisallowedQuery(BadRequestException):
    pass
