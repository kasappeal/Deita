import { Flex, Spinner } from '@chakra-ui/react'
import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

import { useAuth } from '../contexts/AuthContext'


const HomePage: React.FC = () => {
  const { loading, workspace } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!loading && workspace?.id) {
      navigate(`/workspaces/${workspace.id}`, { replace: true })
    }
  }, [loading, workspace, navigate])

  // Always show spinner on root
  return (
    <Flex minH="60vh" align="center" justify="center">
      <Spinner size="xl" color="blue.500" />
    </Flex>
  )
}

export default HomePage
