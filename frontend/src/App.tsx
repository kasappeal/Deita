
import { Box, Container } from '@chakra-ui/react'
import { useEffect } from 'react'
import { Route, Routes } from 'react-router-dom'
import Header from './components/common/Header'
import { useAuth } from './contexts/AuthContext'
import HomePage from './pages/HomePage'
import WorkspacePage from './pages/WorkspacePage'
import WorkspacesRedirectPage from './pages/WorkspacesRedirectPage'

function App() {
  const { workspace } = useAuth();
  useEffect(() => {
    if (workspace && workspace.name) {
      document.title = `${workspace.name} - Deita`;
    } else {
      document.title = 'Deita - Data exploration for humans';
    }
  }, [workspace]);
  return (
    <Box minH="100vh" bg="gray.50" display="flex" flexDirection="column">
      <Header />
      <Container maxW="full" p={0} flex={1} display="flex" flexDirection="column">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/workspaces" element={<WorkspacesRedirectPage />} />
          <Route path="/workspaces/:workspaceId" element={<WorkspacePage />} />
        </Routes>
      </Container>
    </Box>
  )
}

export default App
