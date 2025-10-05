import { Box, Button, Container, Flex, FormControl, FormLabel, Heading, Input, Spinner, Text, VStack, useToast } from '@chakra-ui/react'
import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { useAuth } from '../contexts/AuthContext'
import { Workspace, workspaceApi } from '../services/api'

const WorkspacesPage: React.FC = () => {
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const toast = useToast()
  const [loading, setLoading] = useState(true)
  const [workspaces, setWorkspaces] = useState<Workspace[]>([])
  const [workspaceName, setWorkspaceName] = useState('')
  const [creating, setCreating] = useState(false)

  // Generate random workspace name
  const randomWorkspaceName = () => {
    const animals = ['Otter', 'Fox', 'Bear', 'Hawk', 'Wolf', 'Lynx', 'Seal', 'Crane', 'Swan', 'Panda'];
    const colors = ['Blue', 'Green', 'Red', 'Yellow', 'Purple', 'Orange', 'Silver', 'Gold', 'Indigo', 'Teal'];
    return `${colors[Math.floor(Math.random()*colors.length)]} ${animals[Math.floor(Math.random()*animals.length)]}`;
  }

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/', { replace: true })
      return
    }

    // Load workspaces
    workspaceApi.getWorkspaces()
      .then(setWorkspaces)
      .catch(() => {
        toast({
          title: 'Error loading workspaces',
          status: 'error',
          duration: 3000,
        })
      })
      .finally(() => setLoading(false))

    // Set random name
    setWorkspaceName(randomWorkspaceName())
  }, [isAuthenticated, navigate, toast])

  const handleCreateWorkspace = async () => {
    if (!workspaceName.trim()) return

    setCreating(true)
    try {
      const workspace = await workspaceApi.createWorkspace(workspaceName.trim())
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

  const handleWorkspaceClick = (workspaceId: string) => {
    localStorage.setItem('lastVisitedWorkspaceId', workspaceId)
    navigate(`/workspaces/${workspaceId}`)
  }

  if (loading) {
    return (
      <Flex minH="60vh" align="center" justify="center">
        <Spinner size="xl" color="blue.500" />
      </Flex>
    )
  }

  return (
    <Container maxW="4xl" py={8}>
      <VStack spacing={8} align="stretch">
        <Heading size="lg" textAlign="center">
          {workspaces.length > 0 ? 'Your Workspaces' : 'Create Your First Workspace'}
        </Heading>

        {workspaces.length > 0 ? (
          <VStack spacing={4} align="stretch">
            {workspaces.map(workspace => (
              <Box
                key={workspace.id}
                p={4}
                borderWidth={1}
                borderRadius="md"
                cursor="pointer"
                _hover={{ bg: 'gray.50' }}
                onClick={() => handleWorkspaceClick(workspace.id)}
              >
                <Heading size="md">{workspace.name}</Heading>
                <Text color="gray.600" fontSize="sm">
                  Created {new Date(workspace.created_at).toLocaleDateString()}
                </Text>
              </Box>
            ))}
          </VStack>
        ) : (
          <VStack spacing={4} align="stretch" maxW="md" mx="auto">
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
            >
              Create Workspace
            </Button>
          </VStack>
        )}
      </VStack>
    </Container>
  )
}

export default WorkspacesPage