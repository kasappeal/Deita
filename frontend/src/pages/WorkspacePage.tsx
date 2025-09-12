import { Alert, AlertIcon, Box, Flex, Heading, Spinner, VStack } from '@chakra-ui/react';
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
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
      </Box>
      {/* TODO: Add workspace data preview, image header, etc. */}
    </VStack>
  );
};

export default WorkspacePage;
