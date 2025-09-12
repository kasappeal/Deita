# Deita - Data Exploration and AI-Powered Analysis Platform

Deita is a web-based platform that empowers small business owners and students to extract, explore, and analyze data from Excel and CSV files without requiring advanced technical skills. The platform combines intuitive data exploration with AI-powered SQL generation and natural language explanations.

## 🚀 Features

- **Drag-and-drop file upload** for Excel and CSV files
- **Interactive data exploration** with tabular views
- **AI-powered SQL generation** from natural language questions
- **Natural language explanations** of query results
- **Workspace management** with public sharing capabilities
- **Magic link authentication** for seamless user experience
- **Export capabilities** for query results
- **Responsive design** for desktop, tablet, and mobile

## 🏗️ Architecture

Deita follows a modern, scalable architecture:

- **Backend**: FastAPI (Python) with Clean Architecture patterns
- **Frontend**: React with TypeScript and Chakra UI
- **Database**: PostgreSQL for metadata, DuckDB for analytics
- **Storage**: S3-compatible object storage (MinIO in development)
- **AI**: Integrated AI service for SQL generation and explanations
- **Authentication**: Magic link email authentication
- **Analytics**: Posthog for user behavior tracking

## 🛠️ Technology Stack

### Backend

- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for PostgreSQL
- **Alembic** - Database migrations
- **DuckDB** - Fast analytical queries
- **Pydantic** - Data validation
- **uv** - Fast Python package management

### Frontend

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Fast build tool
  Deita follows a modern, scalable architecture and supports two development workflows.
- **React Query** - Server state management
- **React Router** - Client-side routing

### Infrastructure

- **Docker** - Containerization
- **MailHog** - Email testing (development)

## 📖 Documentation

- [System Architecture](docs/01-system-architecture.md)
- [Technology Stack](docs/02-technology-stack.md)
- [Development Environment](docs/11-dev-environment.md)
- [API Documentation](http://localhost:8000/docs) (when running)

## 🏷️ Versioning

This project uses [Semantic Versioning](https://semver.org/). Version numbers follow the format: `MAJOR.MINOR.PATCH`

## 🆘 Support

- 📖 Check the [documentation](docs/) for detailed information
- 🐛 Report bugs via [GitHub Issues](https://github.com/kasappeal/deita/issues)
