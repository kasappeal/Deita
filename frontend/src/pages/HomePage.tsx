import { Flex, Spinner } from '@chakra-ui/react'
import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

import { useAuth } from '../contexts/AuthContext'


const HomePage: React.FC = () => {
  const { loading, isAuthenticated } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!loading) {
      if (isAuthenticated) {
        // Authenticated user - go to workspaces list
        navigate('/workspaces', { replace: true })
      } else {
        // Anonymous user - check for last visited workspace
        const lastVisitedWorkspaceId = localStorage.getItem('lastVisitedWorkspaceId')
        if (lastVisitedWorkspaceId) {
          navigate(`/workspaces/${lastVisitedWorkspaceId}`, { replace: true })
        } else {
          navigate('/create-workspace', { replace: true })
        }
      }
    }
  }, [loading, isAuthenticated, navigate])

  // Always show spinner on root
  return (
    <Flex minH="60vh" align="center" justify="center">
      <Spinner size="xl" color="blue.500" />
    </Flex>
  )
}

export default HomePage
