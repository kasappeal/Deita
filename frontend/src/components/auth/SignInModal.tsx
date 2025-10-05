import {
    Alert,
    AlertIcon,
    Button,
    FormControl,
    FormLabel,
    Input,
    Modal,
    ModalBody,
    ModalCloseButton,
    ModalContent,
    ModalHeader,
    ModalOverlay,
    Text,
    useToast,
    VStack,
} from '@chakra-ui/react';
import React, { useState } from 'react';
import apiClient from '../../services/api';

interface SignInModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const SignInModal: React.FC<SignInModalProps> = ({ isOpen, onClose }) => {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSent, setIsSent] = useState(false);
  const toast = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;

    setIsLoading(true);
    try {
      await apiClient.post('/v1/auth/magic-link', { email: email.trim() });
      setIsSent(true);
      toast({
        title: 'Magic link sent!',
        description: 'Check your email for the login link.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (error) {
      const errorMessage = error && typeof error === 'object' && 'response' in error
        ? (error as { response?: { data?: { error?: string } } }).response?.data?.error || 'Something went wrong'
        : 'Something went wrong';
      toast({
        title: 'Error sending magic link',
        description: errorMessage,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    setEmail('');
    setIsSent(false);
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} size="md">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Sign In</ModalHeader>
        <ModalCloseButton />
        <ModalBody pb={6}>
          {isSent ? (
            <Alert status="success" borderRadius="md">
              <AlertIcon />
              <VStack align="start" spacing={1}>
                <Text fontWeight="bold">Magic link sent!</Text>
                <Text fontSize="sm">
                  Check your email for the login link. You can close this window.
                </Text>
              </VStack>
            </Alert>
          ) : (
            <form onSubmit={handleSubmit}>
              <VStack spacing={4}>
                <FormControl isRequired>
                  <FormLabel>Email address</FormLabel>
                  <Input
                    type="email"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </FormControl>
                <Button
                  type="submit"
                  colorScheme="blue"
                  width="full"
                  isLoading={isLoading}
                  loadingText="Sending..."
                >
                  Send Magic Link
                </Button>
              </VStack>
            </form>
          )}
        </ModalBody>
      </ModalContent>
    </Modal>
  );
};

export default SignInModal;