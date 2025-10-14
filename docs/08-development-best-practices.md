# Development Best Practices

## Overview

Deita's development process emphasizes code quality, maintainability, security, and rapid iteration. The following practices reflect actual tools and workflows used in the project.

## Development Environment

### Quick Start

```bash
# Clone and enter dev container (recommended)
git clone https://github.com/kasappeal/deita.git
cd deita
code .  # VS Code will prompt to reopen in container

# Or manual setup
cd backend && uv sync
cd ../frontend && npm install
docker-compose -f docker-compose.dev.yml up -d
```

### Tools & Environment

- **Dev Container**: VS Code Dev Containers for consistent environment
- **Python**: 3.11+ with uv package manager (fast, modern)
- **Node.js**: 22+ with npm
- **Docker**: Docker Compose for service orchestration
- **VS Code Extensions**: Auto-installed in dev container (Python, ESLint, Prettier)

## Coding Standards

### Python (Backend)

**Linting & Formatting:**

- **Ruff 0.13+**: Fast all-in-one linter and formatter (replaces Black, isort, Flake8)
- Configuration: `pyproject.toml` with `[tool.ruff]`
- Run: `make lint` or `cd backend && uv run ruff check .`
- Fix: `make format` or `cd backend && uv run ruff format .`

**Style Guidelines:**

- PEP8 compliant (enforced by Ruff)
- Type hints for function signatures (Pydantic for schemas)
- Docstrings for public functions/classes
- Max line length: 100 characters
- Import sorting: stdlib → third-party → local

**Architecture:**

- Clean Architecture: Separation of API, services, models
- Dependency Injection: Use FastAPI's dependency system
- Async/Await: Use async for I/O-bound operations
- Pydantic: Use for all request/response validation

**Example:**

```python
# Good: Clean, typed, async
async def get_workspace(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
) -> Workspace:
    """Retrieve workspace by ID with access control.

    Args:
        workspace_id: UUID of workspace to retrieve
        db: Database session
        current_user: Optional authenticated user

    Returns:
        Workspace object if found and accessible

    Raises:
        HTTPException: 404 if not found or not accessible
    """
    workspace = await workspace_service.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    if workspace.visibility == "private" and workspace.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return workspace
```

### TypeScript/React (Frontend)

**Linting & Formatting:**

- **ESLint 9.17+**: TypeScript-aware linting
- **Prettier 3.4+**: Code formatting
- **TypeScript 5.3+**: Strict mode enabled
- Configuration: `eslint.config.ts`, `.prettierrc`
- Run: `cd frontend && npm run lint`
- Fix: `cd frontend && npm run lint:fix`

**Style Guidelines:**

- Strict TypeScript (no `any` types)
- Functional components with hooks
- Props interfaces for all components
- Consistent file naming: PascalCase for components, camelCase for utilities
- Max line length: 100 characters

**Architecture:**

- Component-based structure by feature
- React Context API for global state (auth, workspace)
- React Query for server state
- Custom hooks for reusable logic
- Axios with interceptors for API calls

**Example:**

```typescript
// Good: Typed, clear, reusable
interface WorkspaceCardProps {
  workspace: Workspace;
  onDelete: (id: string) => Promise<void>;
  isOwner: boolean;
}

export const WorkspaceCard: React.FC<WorkspaceCardProps> = ({
  workspace,
  onDelete,
  isOwner,
}) => {
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await onDelete(workspace.id);
    } catch (error) {
      console.error("Failed to delete workspace:", error);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <Card>
      <CardHeader>{workspace.name}</CardHeader>
      {isOwner && (
        <Button onClick={handleDelete} isLoading={isDeleting}>
          Delete
        </Button>
      )}
    </Card>
  );
};
```

## Testing

### Backend Testing (Pytest)

**Test Structure:**

```
backend/app/tests/
├── conftest.py          # Fixtures and test configuration
├── test_auth_endpoints.py
├── test_workspace_endpoints.py
├── test_query_service.py
└── test_ai_service_chat.py
```

**Running Tests:**

```bash
# All tests with coverage
make test-be
# Or: cd backend && uv run pytest --cov=app --cov-report=html

# Specific test file
cd backend && uv run pytest app/tests/test_auth_endpoints.py

# Specific test function
cd backend && uv run pytest app/tests/test_auth_endpoints.py::test_magic_link_request
```

**Best Practices:**

- Use pytest fixtures for database, client, user setup
- Mock external dependencies (S3, AI service, email)
- Test both success and error cases
- Use `pytest.mark.asyncio` for async tests
- Aim for >80% coverage on critical paths

**Example:**

```python
@pytest.mark.asyncio
async def test_create_workspace(client, auth_headers):
    """Test workspace creation with authentication."""
    response = await client.post(
        "/v1/workspaces",
        json={"name": "Test Workspace", "visibility": "private"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Workspace"
    assert data["visibility"] == "private"
```

### Frontend Testing (Jest + React Testing Library)

**Test Structure:**

```
frontend/src/
├── components/
│   └── workspace/
│       ├── WorkspaceCard.tsx
│       └── WorkspaceCard.test.tsx
└── __tests__/
    └── integration/
```

**Running Tests:**

```bash
# All tests with coverage
make test-fe
# Or: cd frontend && npm test

# Watch mode
cd frontend && npm test -- --watch

# Coverage report
cd frontend && npm test -- --coverage
```

**Best Practices:**

- Use React Testing Library (user-centric testing)
- Mock API calls with MSW (Mock Service Worker)
- Test user interactions, not implementation details
- Use `screen.getByRole` over `getByTestId`
- Test accessibility (ARIA roles, labels)

**Example:**

```typescript
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { WorkspaceCard } from "./WorkspaceCard";

describe("WorkspaceCard", () => {
  it("calls onDelete when delete button is clicked", async () => {
    const mockDelete = jest.fn().mockResolvedValue(undefined);
    const workspace = { id: "123", name: "Test Workspace" };

    render(
      <WorkspaceCard
        workspace={workspace}
        onDelete={mockDelete}
        isOwner={true}
      />
    );

    const deleteButton = screen.getByRole("button", { name: /delete/i });
    fireEvent.click(deleteButton);

    await waitFor(() => {
      expect(mockDelete).toHaveBeenCalledWith("123");
    });
  });
});
```

### Integration Testing

**Not Yet Implemented (Technical Debt):**

- Playwright E2E tests for critical user flows
- API integration tests against real database
- Cross-browser testing

## Documentation

### Code Documentation

**Python:**

- Docstrings for all public functions/classes (Google style)
- Type hints for function signatures
- Inline comments for complex logic only

**TypeScript:**

- JSDoc comments for exported functions
- Interface documentation for complex types
- Comments for non-obvious business logic

### Project Documentation

**Architecture Docs** (`docs/`):

- 01-system-architecture.md
- 02-technology-stack.md
- 03-data-model-design.md
- 04-api-design.md
- 05-service-boundaries.md
- 06-performance-scalability.md
- 07-security.md
- 08-development-best-practices.md (this file)
- 09-deployment-best-practices.md
- 10-risk-assessment-technical-debt.md
- 11-dev-environment.md

**API Documentation:**

- OpenAPI/Swagger: Auto-generated at `/docs` endpoint
- Pydantic schemas provide type documentation
- Manual API docs in `04-api-design.md`

**Onboarding:**

- README.md: Quick start, features, tech stack
- 11-dev-environment.md: Detailed setup instructions

## Git Workflow

### Branch Strategy

```
main (production-ready)
└── develop (integration branch)
    ├── feature/workspace-chat
    ├── feature/csv-export
    └── fix/query-timeout-handling
```

### Commit Messages

Follow conventional commits:

```
feat(workspace): add chat message persistence
fix(auth): handle expired JWT tokens gracefully
docs(api): update query endpoint documentation
refactor(query): extract SQL validation logic
test(workspace): add file upload integration tests
chore(deps): update FastAPI to 0.116.0
```

### Pull Request Process

1. **Create feature branch** from `develop`
2. **Write tests** for new functionality
3. **Ensure tests pass** (`make test`)
4. **Lint code** (`make lint`)
5. **Create PR** with description and testing notes
6. **Request review** from at least one team member
7. **Address feedback** and re-request review
8. **Merge** after approval and CI passes

### CI/CD Pipeline (GitHub Actions)

**Automated Checks:**

- Lint: Ruff (backend), ESLint (frontend)
- Format: Ruff (backend), Prettier (frontend)
- Tests: Pytest (backend), Jest (frontend)
- Type Check: TypeScript compilation
- Security: Dependency vulnerability scanning

**Deployment:**

- `main` branch: Auto-deploy to production (after manual approval)
- `develop` branch: Auto-deploy to staging environment
- Feature branches: Run tests only

## Security & Privacy

### Secret Management

**Never Commit:**

- API keys, passwords, JWT secrets
- Database credentials
- S3 access keys
- Email service credentials

**Best Practices:**

- Use `.env` files (excluded via `.gitignore`)
- Docker secrets for production
- Environment variables for all config
- Rotate secrets regularly

### Input Validation

**Backend:**

- Pydantic schemas for all request bodies
- SQL injection prevention: parameterized queries only
- File upload validation: size, type, content
- Rate limiting: SlowAPI (100 req/min default)

**Frontend:**

- Form validation: React Hook Form + Zod
- XSS prevention: React's built-in escaping
- CSRF protection: JWT in headers (not cookies)

### Dependency Security

```bash
# Check for vulnerabilities
cd backend && uv run pip-audit
cd frontend && npm audit

# Update dependencies
cd backend && uv sync --upgrade
cd frontend && npm update
```

## Code Review Guidelines

### For Reviewers

**Check:**

- [ ] Code follows style guidelines (Ruff/ESLint passes)
- [ ] Tests exist and pass for new functionality
- [ ] No secrets or sensitive data committed
- [ ] API contracts match documentation
- [ ] Error handling is comprehensive
- [ ] Performance implications considered
- [ ] Security implications reviewed
- [ ] Documentation updated if needed

**Provide:**

- Constructive feedback with specific suggestions
- Praise for good practices
- Questions for unclear logic
- Alternative approaches when appropriate

### For Authors

**Before Requesting Review:**

- [ ] Self-review your changes
- [ ] Run `make lint` and `make format`
- [ ] Run `make test` and ensure all pass
- [ ] Update documentation if API/behavior changed
- [ ] Write clear PR description with context
- [ ] Link related issues

**After Feedback:**

- Respond to all comments (resolve or discuss)
- Make requested changes
- Re-request review when ready

## Performance Optimization

### Backend

**Profile Before Optimizing:**

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
# Your code here
profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 slowest functions
```

**Common Optimizations:**

- Use async/await for I/O operations
- Batch database queries
- Cache expensive computations (Redis)
- Stream large responses (CSV export)
- Index frequently queried columns

### Frontend

**Tools:**

- React DevTools Profiler
- Lighthouse for performance audits
- Network tab for API call analysis

**Common Optimizations:**

- Memoize expensive computations (`useMemo`)
- Avoid unnecessary re-renders (`React.memo`)
- Lazy load routes (`React.lazy`)
- Debounce user input
- Virtualize long lists

## Debugging

### Backend

**Logging:**

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Workspace created", extra={"workspace_id": workspace.id})
logger.error("Query execution failed", exc_info=True)
```

**Interactive Debugger:**

```python
import pdb; pdb.set_trace()  # Breakpoint
# Or use VS Code debugger (configured in .vscode/launch.json)
```

### Frontend

**Browser DevTools:**

- Console: `console.log`, `console.error`, `console.table`
- Network: Inspect API calls and responses
- React DevTools: Component hierarchy and props
- Redux DevTools: State management (if using Redux)

**VS Code Debugger:**

- Set breakpoints in TypeScript files
- Launch Chrome with debugging enabled
- Step through code execution

## Continuous Improvement

### Refactoring Guidelines

**When to Refactor:**

- Code is duplicated in 3+ places
- Function is longer than 50 lines
- Class has more than 5 dependencies
- Test coverage is <60%
- Code smell identified in review

**How to Refactor:**

1. **Write tests** for existing behavior (if missing)
2. **Make small changes** incrementally
3. **Run tests** after each change
4. **Commit frequently** with descriptive messages
5. **Review changes** before merging

### Technical Debt Management

- Track debt in `10-risk-assessment-technical-debt.md`
- Prioritize: High → Medium → Low
- Allocate 20% of sprint capacity to debt reduction
- Review debt quarterly and re-prioritize

### Learning & Knowledge Sharing

- Code review as teaching opportunity
- Document patterns and anti-patterns
- Share interesting bugs/solutions in team meetings
- Contribute to architecture documentation

## Extensibility

### Design Principles

- **SOLID**: Single responsibility, Open/closed, Liskov substitution, Interface segregation, Dependency inversion
- **DRY**: Don't Repeat Yourself (but avoid premature abstraction)
- **KISS**: Keep It Simple, Stupid
- **YAGNI**: You Aren't Gonna Need It (avoid over-engineering)

### Future-Proofing

- **Microservices**: Clean service boundaries enable extraction
- **API Versioning**: All endpoints under `/v1/` for future v2
- **Database Migrations**: Alembic for schema evolution
- **Feature Flags**: Enable gradual rollout and A/B testing
- **External Integrations**: Abstract third-party services behind interfaces
