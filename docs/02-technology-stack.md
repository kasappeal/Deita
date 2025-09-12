# Technology Stack

## Overview

The technology stack for Deita is selected for rapid development, maintainability, and scalability, with a focus on Python for backend analytics and React for a modern, responsive frontend.

## Frontend

- **Framework:** React (SPA)
- **Language:** TypeScript
- **UI Library:** Chakra UI
- **State Management:** React Context, Redux Toolkit (if needed)
- **Build Tool:** Vite
- **Testing:** Jest, React Testing Library, Playwright (E2E)
- **Linting/Formatting:** ESLint, Prettier

## Backend

- **Framework:** FastAPI (Python)
- **Language:** Python 3.12+
- **Database:**
  - **Metadata & persistence:** PostgreSQL
  - **Analytical queries:** DuckDB (OLAP, in-process)
- **File Storage:**
  - **Development:** Local filesystem
  - **Production:** S3-compatible object storage (e.g., Hertzner Storage Box)
- **AI Model:** In-house model (LLM for SQL generation, explanations, relationships)
- **Authentication:** Magic link via email (using FastAPI + email service)
- **Analytics:** Posthog (event tracking)
- **Testing:** Pytest, Coverage.py
- **Linting/Formatting:** Ruff

## DevOps & Deployment

- **Containerization:** Docker (multi-stage builds, Compose)
- **CI/CD:** GitHub Actions
- **Hosting:** Hertzner Cloud (VMs, Storage Box)
- **Secrets Management:** Docker secrets, environment variables
- **Monitoring:** Posthog, Prometheus (optional)

## Other Tools

- **Documentation:** MkDocs, Markdown, Mermaid, PlantUML
- **Diagrams:** PlantUML, MermaidJS
- **Error Reporting:** Posthog (custom events)

## Rationale

- **Python + DuckDB:** Enables fast, flexible analytics on user-uploaded data without external dependencies.
- **React SPA:** Delivers a modern, responsive UI for all device types.
- **PostgreSQL:** Reliable, scalable metadata storage.
- **Docker:** Ensures reproducible, portable deployments.
- **GitHub Actions:** Automates testing and deployment.
