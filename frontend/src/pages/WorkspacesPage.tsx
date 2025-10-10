import { AlertDialog, AlertDialogBody, AlertDialogContent, AlertDialogFooter, AlertDialogHeader, AlertDialogOverlay, Box, Button, CircularProgress, CircularProgressLabel, Container, Flex, FormControl, FormLabel, Heading, HStack, Icon, IconButton, Input, Spinner, Text, Tooltip, useDisclosure, useToast, VStack } from '@chakra-ui/react'
import React, { useEffect, useRef, useState } from 'react'
import { FiGlobe, FiLock, FiTrash2 } from 'react-icons/fi'
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
  const [workspaceToDelete, setWorkspaceToDelete] = useState<Workspace | null>(null)
  const [deleting, setDeleting] = useState(false)
  const { isOpen, onOpen, onClose } = useDisclosure()
  const cancelRef = useRef<HTMLButtonElement>(null)

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

  // Clear workspace context when on workspaces list page
  const { setWorkspace } = useAuth()
  useEffect(() => {
    setWorkspace(null)
  }, [setWorkspace])

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

  const handleDeleteClick = (workspace: Workspace, event: React.MouseEvent) => {
    event.stopPropagation() // Prevent workspace navigation
    setWorkspaceToDelete(workspace)
    onOpen()
  }

  const handleDeleteConfirm = async () => {
    if (!workspaceToDelete) return

    setDeleting(true)
    try {
      await workspaceApi.deleteWorkspace(workspaceToDelete.id)
      setWorkspaces(workspaces => workspaces.filter(w => w.id !== workspaceToDelete.id))
      toast({
        title: 'Workspace deleted successfully',
        status: 'success',
        duration: 3000,
      })
    } catch (error) {
      toast({
        title: 'Error deleting workspace',
        status: 'error',
        duration: 3000,
      })
    } finally {
      setDeleting(false)
      setWorkspaceToDelete(null)
      onClose()
    }
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
        {workspaces.length > 0 ? (
          <VStack spacing={4} align="stretch">
            {workspaces.map(workspace => {
              const used = workspace.storage_used ?? 0;
              const max = workspace.max_storage ?? 1;
              const percent = Math.min(100, Math.round((used / max) * 100));
              const tooltipLabel = `Storage: ${percent}% - ${(used / (1024 * 1024)).toFixed(0)} of ${(max / (1024 * 1024)).toFixed(0)} MB`;
              
              return (
                <Box
                  key={workspace.id}
                  p={4}
                  borderWidth={1}
                  borderRadius="md"
                  cursor="pointer"
                  bg="white"
                  _hover={{ bg: 'gray.50' }}
                  onClick={() => handleWorkspaceClick(workspace.id)}
                >
                  <Flex justify="space-between" align="center">
                    <Box flex={1}>
                      <HStack spacing={2} align="center" mb={1}>
                        <Heading size="md">{workspace.name}</Heading>
                        <Tooltip 
                          label={workspace.visibility === 'private' ? 'Private workspace' : 'Public workspace'} 
                          hasArrow
                        >
                          <Box>
                            <Icon
                              as={workspace.visibility === 'private' ? FiLock : FiGlobe}
                              color={workspace.visibility === 'private' ? 'red.500' : 'green.500'}
                              size="16px"
                            />
                          </Box>
                        </Tooltip>
                      </HStack>
                      <Text color="gray.600" fontSize="xs">
                        Created {new Date(workspace.created_at).toLocaleDateString()}
                      </Text>
                    </Box>
                    <HStack spacing={2}>
                      <Tooltip label={tooltipLabel} hasArrow>
                        <CircularProgress 
                          value={percent} 
                          size="40px" 
                          thickness="8px" 
                          color={percent > 90 ? 'red.400' : 'blue.400'} 
                        >
                          <CircularProgressLabel>{percent}%</CircularProgressLabel>
                        </CircularProgress>
                      </Tooltip>
                      <Tooltip label="Delete workspace" hasArrow>
                        <IconButton
                          aria-label="Delete workspace"
                          icon={<FiTrash2 />}
                          size="sm"
                          colorScheme="red"
                          variant="ghost"
                          onClick={(e) => handleDeleteClick(workspace, e)}
                        />
                      </Tooltip>
                    </HStack>
                  </Flex>
                </Box>
              );
            })}
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

      <AlertDialog
        isOpen={isOpen}
        leastDestructiveRef={cancelRef}
        onClose={onClose}
      >
        <AlertDialogOverlay>
          <AlertDialogContent>
            <AlertDialogHeader fontSize="lg" fontWeight="bold">
              Delete Workspace
            </AlertDialogHeader>

            <AlertDialogBody>
              Are you sure you want to delete &ldquo;{workspaceToDelete?.name}&rdquo;? This action cannot be undone and will permanently remove all files and data in this workspace.
            </AlertDialogBody>

            <AlertDialogFooter>
              <Button ref={cancelRef} onClick={onClose}>
                Cancel
              </Button>
              <Button 
                colorScheme="red" 
                onClick={handleDeleteConfirm} 
                ml={3}
                isLoading={deleting}
                loadingText="Deleting..."
              >
                Delete
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>
    </Container>
  )
}

export default WorkspacesPage