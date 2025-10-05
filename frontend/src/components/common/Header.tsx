import { Box, Button, Link as ChakraLink, Flex, Heading, HStack, Text } from '@chakra-ui/react';
import React, { useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';

import { useAuth } from '../../contexts/AuthContext';
import SignInModal from '../auth/SignInModal';

const Header: React.FC = () => {
  const { workspace, isAuthenticated, logout, user } = useAuth();
  const [isSignInModalOpen, setIsSignInModalOpen] = useState(false);

  const handleSignInClick = () => {
    setIsSignInModalOpen(true);
  };

  const handleLogoutClick = () => {
    logout();
  };

  return (
    <>
      <Box bg="white" shadow="sm" borderBottom="1px" borderColor="gray.200">
        <Flex maxW="full" mx="auto" p={4} justify="space-between" align="center">
          {/* Logo */}
          <ChakraLink as={RouterLink} to="/" _hover={{ textDecoration: 'none' }}>
            <Heading as="h1" size="lg" color="blue.600">
              Deita
            </Heading>
          </ChakraLink>

          {/* Workspace name and auth buttons */}
          <HStack>
            {workspace && (
              <>
                <Text fontWeight="bold" color="gray.700" fontSize="md" data-testid="workspace-header-name">
                  {workspace.name}
                </Text>
                <Text fontSize="sm" color="gray.500" bg="gray.100" px={2} py={1} borderRadius="md">
                  {workspace.storage_used !== undefined && workspace.max_storage !== undefined
                    ? `${(workspace.storage_used / (1024 * 1024)).toFixed(2)} MB / ${(workspace.max_storage / (1024 * 1024)).toFixed(2)} MB`
                    : ''}
                </Text>
              </>
            )}
            {isAuthenticated ? (
              <HStack>
                {user && (
                  <Text fontSize="sm" color="gray.600">
                    {user.name || user.email}
                  </Text>
                )}
                <Button colorScheme="gray" size="sm" onClick={handleLogoutClick}>
                  Logout
                </Button>
              </HStack>
            ) : (
              <Button colorScheme="blue" size="sm" onClick={handleSignInClick}>
                Sign In
              </Button>
            )}
          </HStack>
        </Flex>
      </Box>

      <SignInModal
        isOpen={isSignInModalOpen}
        onClose={() => setIsSignInModalOpen(false)}
      />
    </>
  );
}

export default Header
