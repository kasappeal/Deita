import { Box, Spinner, Text, VStack, useToast } from '@chakra-ui/react';
import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const AuthVerifyPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  const toast = useToast();

  useEffect(() => {
    const token = searchParams.get('token');

    if (!token) {
      toast({
        title: 'Invalid verification link',
        description: 'No token provided in the URL.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      navigate('/');
      return;
    }

    const verifyToken = async () => {
      try {
        await login(token);
        toast({
          title: 'Successfully signed in!',
          description: 'Welcome to Deita.',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
        navigate('/');
      } catch (error) {
        const errorMessage =
          error && typeof error === 'object' && 'response' in error
            ? (error as { response?: { data?: { error?: string } } }).response?.data?.error || 'Failed to verify token.'
            : 'Failed to verify token.';
        toast({
          title: 'Verification failed',
          description: errorMessage,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
        navigate('/');
      }
    };

    verifyToken();
  }, [searchParams, navigate, login, toast]);

  return (
    <Box
      minH="100vh"
      display="flex"
      alignItems="center"
      justifyContent="center"
      bg="gray.50"
    >
      <VStack spacing={4}>
        <Spinner size="xl" color="blue.500" />
        <Text fontSize="lg" color="gray.600">
          Verifying your sign in...
        </Text>
      </VStack>
    </Box>
  );
};

export default AuthVerifyPage;