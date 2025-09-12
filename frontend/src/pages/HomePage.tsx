import {
    Alert,
    AlertIcon,
    Badge,
    Box,
    Button,
    Card,
    CardBody,
    CardHeader,
    Flex,
    Heading,
    HStack,
    Spinner,
    Text,
    useToast,
    VStack,
} from '@chakra-ui/react'
import React, { useState } from 'react'
import { useQuery } from 'react-query'
import apiClient from '../services/api'

interface HelloWorldResponse {
  message: string
  version: string
  environment: string
}

interface HealthCheckResponse {
  status: string
  message: string
  version: string
  timestamp: string
}

const HomePage: React.FC = () => {
  const toast = useToast()
  const [greeting, setGreeting] = useState<string>('')

  // Query for hello world
  const {
    data: helloData,
    isLoading: helloLoading,
    error: helloError
  } = useQuery<HelloWorldResponse>(
    'hello-world',
    () => apiClient.get('/v1/').then(res => res.data),
    {
      onSuccess: (data) => {
        setGreeting(`Hello from ${data.environment} environment! 🚀`)
      }
    }
  )

  // Query for health check
  const {
    data: healthData,
    isLoading: healthLoading,
    error: healthError
  } = useQuery<HealthCheckResponse>(
    'health-check',
    () => apiClient.get('/v1/health').then(res => res.data),
    {
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  )

  const handleTestConnection = () => {
    toast({
      title: 'Connection Test',
      description: 'Testing connection to backend...',
      status: 'info',
      duration: 2000,
      isClosable: true,
    })
  }

  return (
    <VStack spacing={8} align="stretch">
      {/* Hero Section */}
      <Box textAlign="center" py={10}>
        <Heading as="h1" size="2xl" mb={4} color="blue.600">
          Welcome to Deita
        </Heading>
        <Text fontSize="xl" color="gray.600" maxW="600px" mx="auto">
          Your intelligent data exploration and AI-powered SQL assistance platform
        </Text>
      </Box>

      {/* Status Cards */}
      <HStack spacing={6} align="stretch">
        {/* Hello World Card */}
        <Card flex={1}>
          <CardHeader>
            <Heading size="md">Backend Connection</Heading>
          </CardHeader>
          <CardBody>
            {helloLoading ? (
              <Flex justify="center" py={4}>
                <Spinner color="blue.500" />
              </Flex>
            ) : helloError ? (
              <Alert status="error">
                <AlertIcon />
                Failed to connect to backend
              </Alert>
            ) : helloData ? (
              <VStack align="start" spacing={3}>
                <Text>{helloData.message}</Text>
                <HStack>
                  <Badge colorScheme="blue">v{helloData.version}</Badge>
                  <Badge colorScheme={helloData.environment === 'development' ? 'yellow' : 'green'}>
                    {helloData.environment}
                  </Badge>
                </HStack>
                <Text fontSize="sm" color="gray.600">
                  {greeting}
                </Text>
              </VStack>
            ) : null}
          </CardBody>
        </Card>

        {/* Health Check Card */}
        <Card flex={1}>
          <CardHeader>
            <Heading size="md">System Health</Heading>
          </CardHeader>
          <CardBody>
            {healthLoading ? (
              <Flex justify="center" py={4}>
                <Spinner color="green.500" />
              </Flex>
            ) : healthError ? (
              <Alert status="error">
                <AlertIcon />
                Health check failed
              </Alert>
            ) : healthData ? (
              <VStack align="start" spacing={3}>
                <HStack>
                  <Badge colorScheme={healthData.status === 'healthy' ? 'green' : 'red'}>
                    {healthData.status}
                  </Badge>
                  <Text fontSize="sm" color="gray.600">
                    Last checked: {new Date(healthData.timestamp).toLocaleTimeString()}
                  </Text>
                </HStack>
                <Text fontSize="sm">{healthData.message}</Text>
              </VStack>
            ) : null}
          </CardBody>
        </Card>
      </HStack>

      {/* Action Buttons */}
      <Box textAlign="center" py={6}>
        <VStack spacing={4}>
          <Text fontSize="lg" color="gray.700">
            Ready to start exploring your data?
          </Text>
          <HStack spacing={4}>
            <Button colorScheme="blue" size="lg" onClick={handleTestConnection}>
              Test Connection
            </Button>
            <Button variant="outline" size="lg" disabled>
              Upload Data (Coming Soon)
            </Button>
          </HStack>
        </VStack>
      </Box>

      {/* Feature Preview */}
      <Card>
        <CardHeader>
          <Heading size="md">What is Coming Next</Heading>
        </CardHeader>
        <CardBody>
          <VStack align="start" spacing={2}>
            <Text>🔍 Interactive data exploration tools</Text>
            <Text>🤖 AI-powered SQL query assistance</Text>
            <Text>📊 Beautiful data visualizations</Text>
            <Text>🔄 Real-time collaboration features</Text>
            <Text>📈 Advanced analytics and insights</Text>
          </VStack>
        </CardBody>
      </Card>
    </VStack>
  )
}

export default HomePage
