
import { Box, Container } from '@chakra-ui/react'
import { useEffect } from 'react'
import { Route, Routes } from 'react-router-dom'
import Header from './components/common/Header'
import { useAuth } from './contexts/AuthContext'
import HomePage from './pages/HomePage'
import WorkspacePage from './pages/WorkspacePage'

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
    <Box minH="100vh" bg="gray.50">
      <Header />
      <Container maxW="container.xl" py={8}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/workspaces/:workspaceId" element={<WorkspacePage />} />
        </Routes>
      </Container>
    </Box>
  )
}

export default App
