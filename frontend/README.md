# Deita

React TypeScript frontend for the Deita data exploration platform.

## Quick Start

### Development Setup

1. **Install dependencies**:

```bash
npm install
```

2. **Create `.env` file**:

```bash
cp .env.example .env
```

3. **Start the development server**:

```bash
npm start
```

The application will be available at http://localhost:3000

## Available Scripts

- `npm start` - Start development server
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run test` - Run tests
- `npm run test:watch` - Run tests in watch mode
- `npm run test:coverage` - Run tests with coverage
- `npm run lint` - Lint code
- `npm run lint:fix` - Fix lint issues
- `npm run type-check` - Run TypeScript type checking

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── common/         # Common components (Header, Footer, etc.)
│   ├── auth/           # Authentication components
│   ├── data/           # Data-related components
│   ├── workspace/      # Workspace components
│   └── ai/             # AI/ML components
├── pages/              # Page components
├── services/           # API services and utilities
├── hooks/              # Custom React hooks
├── contexts/           # React contexts
├── types/              # TypeScript type definitions
├── utils/              # Utility functions
└── __tests__/          # Test files
```

## API Integration

The frontend connects to the backend API at `http://localhost:8000`.

Read [API Design docs](../docs/04-api-design.md) for more info about backend API.

## Testing

The project uses Jest and React Testing Library for testing:

- Unit tests for components
- Integration tests for user flows
- Coverage reporting
