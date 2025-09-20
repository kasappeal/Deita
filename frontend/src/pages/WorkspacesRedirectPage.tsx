import { Flex, Spinner } from '@chakra-ui/react'
import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

import { useAuth } from '../contexts/AuthContext'

const WorkspacesRedirectPage: React.FC = () => {
  const { loading, workspace } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!loading) {
      if (workspace?.id) {
        // If workspace is loaded from localStorage, redirect to its specific page
        navigate(`/workspaces/${workspace.id}`, { replace: true })
      } else {
        // If no workspace in localStorage, redirect to home which will create a new one
        navigate('/', { replace: true })
      }
    }
  }, [loading, workspace, navigate])

  // Show spinner while loading
  return (
    <Flex minH="60vh" align="center" justify="center">
      <Spinner size="xl" color="blue.500" />
    </Flex>
  )
}

export default WorkspacesRedirectPage