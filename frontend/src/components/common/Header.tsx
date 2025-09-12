import { Box, Button, Link as ChakraLink, Flex, Heading, HStack, Text } from '@chakra-ui/react';
import React from 'react';
import { Link as RouterLink } from 'react-router-dom';

import { useAuth } from '../../contexts/AuthContext';

const Header: React.FC = () => {
  const { workspace } = useAuth();
  return (
    <Box bg="white" shadow="sm" borderBottom="1px" borderColor="gray.200">
      <Flex maxW="container.xl" mx="auto" px={4} py={4} justify="space-between" align="center">
        {/* Logo */}
        <ChakraLink as={RouterLink} to="/" _hover={{ textDecoration: 'none' }}>
          <Heading as="h1" size="lg" color="blue.600">
            Deita
          </Heading>
        </ChakraLink>

        {/* Workspace name at right */}
        <HStack spacing={6}>
          {workspace && (
            <Text fontWeight="bold" color="gray.700" fontSize="md" data-testid="workspace-header-name">
              {workspace.name}
            </Text>
          )}
          <Button colorScheme="blue" size="sm">
            Sign In
          </Button>
        </HStack>
      </Flex>
    </Box>
  )
}

export default Header
