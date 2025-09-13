import {
  Alert,
  AlertIcon,
  Box,
  Button,
  Flex,
  Heading,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
  Spinner,
  Text,
  useDisclosure,
  VStack
} from '@chakra-ui/react';
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import FileUploader from '../components/files/FileUploader';
import { useAuth } from '../contexts/AuthContext';
import apiClient from '../services/api';

interface Workspace {
  id: string;
  name: string;
  visibility: string;
  owner?: string;
  created_at?: string;
}

const WorkspacePage: React.FC = () => {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const [loading, setLoading] = useState(true);
  const [workspace, setWorkspaceLocal] = useState<Workspace | null>(null);
  const { setWorkspace } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const { isOpen, onOpen, onClose } = useDisclosure();

  useEffect(() => {
    if (!workspaceId) return;
    setLoading(true);
    apiClient.get(`/v1/workspaces/${workspaceId}`)
      .then(res => {
        setWorkspaceLocal(res.data);
        setWorkspace(res.data);
        setError(null);
      })
      .catch(() => {
        setWorkspaceLocal(null);
        setWorkspace(null);
        setError('Workspace not found.');
      })
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [workspaceId]);

  if (loading) {
    return (
      <Flex minH="60vh" align="center" justify="center">
        <Spinner size="xl" color="blue.500" />
      </Flex>
    );
  }

  if (error) {
    return (
      <Flex minH="60vh" align="center" justify="center">
        <Alert status="error">
          <AlertIcon />
          {error}
        </Alert>
      </Flex>
    );
  }

  if (!workspace) return null;

  return (
    <VStack spacing={8} align="stretch">
      <Box textAlign="center" py={10}>
        <Heading as="h1" size="2xl" mb={4} color="blue.600">
          Workspace: {workspace.name}
        </Heading>
        <Button 
          colorScheme="blue" 
          size="lg" 
          onClick={onOpen}
        >
          Upload Files
        </Button>

        <Modal isOpen={isOpen} onClose={onClose} size="xl">
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>Upload Files</ModalHeader>
            <ModalCloseButton />
            <ModalBody pb={6}>
              <FileUploader 
                workspaceId={workspaceId || ''} 
                onUploadComplete={(updatedWorkspace) => {
                  if (updatedWorkspace) {
                    // Update local workspace state with the updated info from server
                    setWorkspaceLocal(updatedWorkspace);
                    setWorkspace(updatedWorkspace);
                  }
                  onClose(); // Close the modal after successful upload
                }}
              />
            </ModalBody>
          </ModalContent>
        </Modal>
      </Box>
      
      <Box py={6}>
        <Heading size="lg" mb={4}>Your Data</Heading>
        {/* Main workspace content will go here */}
        <Box p={6} bg="white" borderRadius="md" boxShadow="sm">
          <Text>No data available yet. Click the "Upload Files" button to get started.</Text>
        </Box>
      </Box>
    </VStack>
  );
};

export default WorkspacePage;
