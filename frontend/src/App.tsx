import { Box, Container } from '@chakra-ui/react'
import { useEffect } from 'react'
import { Route, Routes, useLocation } from 'react-router-dom'
import Header from './components/common/Header'
import { useAuth } from './contexts/AuthContext'
import AuthVerifyPage from './pages/AuthVerifyPage'
import CreateWorkspacePage from './pages/CreateWorkspacePage'
import HomePage from './pages/HomePage'
import WorkspacePage from './pages/WorkspacePage'
import WorkspacesPage from './pages/WorkspacesPage'

function App() {
  const { workspace } = useAuth();
  const location = useLocation();

  useEffect(() => {
    if (workspace && workspace.name) {
      document.title = `${workspace.name} - Deita`;
    } else {
      document.title = 'Deita - Data exploration for humans';
    }
  }, [workspace]);

  // Don't show header on auth verify page
  const showHeader = location.pathname !== '/auth/verify';

  return (
    <Box minH="100vh" bg="gray.50" display="flex" flexDirection="column">
      {showHeader && <Header />}
      <Container maxW="full" p={0} flex={1} display="flex" flexDirection="column">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/workspaces" element={<WorkspacesPage />} />
          <Route path="/workspaces/:workspaceId" element={<WorkspacePage />} />
          <Route path="/create-workspace" element={<CreateWorkspacePage />} />
          <Route path="/auth/verify" element={<AuthVerifyPage />} />
        </Routes>
      </Container>
    </Box>
  )
}

export default App
