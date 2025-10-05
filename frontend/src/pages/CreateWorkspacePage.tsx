import { Button, Container, FormControl, FormLabel, Heading, Input, Text, VStack, useToast } from '@chakra-ui/react'
import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { useAuth } from '../contexts/AuthContext'
import { workspaceApi } from '../services/api'

const CreateWorkspacePage: React.FC = () => {
  const { isAuthenticated, setWorkspace } = useAuth()
  const navigate = useNavigate()
  const toast = useToast()
  const [workspaceName, setWorkspaceName] = useState('')
  const [creating, setCreating] = useState(false)

  // Generate random workspace name
  const randomWorkspaceName = () => {
    const animals = ['Otter', 'Fox', 'Bear', 'Hawk', 'Wolf', 'Lynx', 'Seal', 'Crane', 'Swan', 'Panda'];
    const colors = ['Blue', 'Green', 'Red', 'Yellow', 'Purple', 'Orange', 'Silver', 'Gold', 'Indigo', 'Teal'];
    return `${colors[Math.floor(Math.random()*colors.length)]} ${animals[Math.floor(Math.random()*animals.length)]}`;
  }

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/workspaces', { replace: true })
      return
    }

    // Set random name
    setWorkspaceName(randomWorkspaceName())
  }, [isAuthenticated, navigate])

  const handleCreateWorkspace = async () => {
    if (!workspaceName.trim()) return

    setCreating(true)
    try {
      const workspace = await workspaceApi.createWorkspace(workspaceName.trim())
      setWorkspace(workspace)
      localStorage.setItem('workspaceId', workspace.id)
      localStorage.setItem('lastVisitedWorkspaceId', workspace.id)
      navigate(`/workspaces/${workspace.id}`, { replace: true })
    } catch (error) {
      toast({
        title: 'Error creating workspace',
        status: 'error',
        duration: 3000,
      })
    } finally {
      setCreating(false)
    }
  }

  return (
    <Container maxW="4xl" py={8}>
      <VStack spacing={8} align="stretch">
        <Heading size="lg" textAlign="center">
          Create Your Workspace
        </Heading>

        <VStack spacing={4} align="stretch" maxW="md" mx="auto">
          <Text textAlign="center" color="gray.600">
            Get started by creating your first workspace for data exploration.
          </Text>

          <FormControl>
            <FormLabel>Workspace Name</FormLabel>
            <Input
              value={workspaceName}
              onChange={(e) => setWorkspaceName(e.target.value)}
              placeholder="Enter workspace name"
            />
          </FormControl>

          <Button
            colorScheme="blue"
            onClick={handleCreateWorkspace}
            isLoading={creating}
            loadingText="Creating..."
            size="lg"
          >
            Create Workspace
          </Button>
        </VStack>
      </VStack>
    </Container>
  )
}

export default CreateWorkspacePage