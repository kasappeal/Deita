import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Box, Container } from '@chakra-ui/react'
import HomePage from './pages/HomePage'
import Header from './components/common/Header'

function App() {
  return (
    <Box minH="100vh" bg="gray.50">
      <Header />
      <Container maxW="container.xl" py={8}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          {/* Add more routes as needed */}
        </Routes>
      </Container>
    </Box>
  )
}

export default App
