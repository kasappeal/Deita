import {
  Alert,
  AlertIcon,
  Flex,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
  Spinner,
  useDisclosure,
  useToast,
  VStack
} from '@chakra-ui/react';
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import TableDataView from '../components/data/TableDataView';
import FileUploader from '../components/files/FileUploader';
import EmptyTableState, { NoFilesState } from '../components/workspace/EmptyTableState';
import TablesSidebar from '../components/workspace/TablesSidebar';
import { useAuth } from '../contexts/AuthContext';
import apiClient, { FileData, workspaceApi } from '../services/api';

interface Workspace {
  id: string;
  name: string;
  visibility: string;
  owner?: string;
  created_at?: string;
  storage_used?: number;
  max_storage?: number;
}

const WorkspacePage: React.FC = () => {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const [loading, setLoading] = useState(true);
  const [filesLoading, setFilesLoading] = useState(true);
  const [workspace, setWorkspaceLocal] = useState<Workspace | null>(null);
  const [files, setFiles] = useState<FileData[]>([]);
  const [selectedTableId, setSelectedTableId] = useState<string | undefined>();
  const { setWorkspace } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [autoOpenUpload, setAutoOpenUpload] = useState(false);
  const toast = useToast();

  // Fetch workspace data
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

  // Fetch files data
  useEffect(() => {
    if (!workspaceId || !workspace) return;
    
    setFilesLoading(true);
    workspaceApi.getFiles(workspaceId)
      .then((filesData) => {
        setFiles(filesData);
        
        // Auto-open upload modal if no files
        if (filesData.length === 0) {
          setAutoOpenUpload(true);
        }
      })
      .catch((err) => {
        console.error('Error fetching files:', err);
        setFiles([]);
        toast({
          title: 'Error fetching files',
          description: 'Could not load workspace files.',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      })
      .finally(() => setFilesLoading(false));
  }, [workspaceId, workspace, toast]);

  // Auto-open upload modal when there are no files
  useEffect(() => {
    if (autoOpenUpload && !filesLoading && files.length === 0) {
      onOpen();
      setAutoOpenUpload(false);
    }
  }, [autoOpenUpload, filesLoading, files.length, onOpen]);

  const handleUploadComplete = (updatedWorkspace?: Workspace) => {
    if (updatedWorkspace) {
      setWorkspaceLocal(updatedWorkspace);
      setWorkspace(updatedWorkspace);
    }
    
    // Refresh files after upload
    if (workspaceId) {
      workspaceApi.getFiles(workspaceId)
        .then(setFiles)
        .catch(console.error);
    }
    
    onClose();
  };

  // Helper function to get table name from selected table ID
  const getSelectedTableName = () => {
    if (!selectedTableId) return null;
    const selectedFile = files.find(file => file.id === selectedTableId);
    return selectedFile ? selectedFile.table_name : null;
  };

  const getSelectedFileName = () => {
    if (!selectedTableId) return null;
    const selectedFile = files.find(file => file.id === selectedTableId);
    return selectedFile ? selectedFile.filename : null;
  };

  if (loading) {
    return (
      <Flex minH="100vh" align="center" justify="center">
        <Spinner size="xl" color="blue.500" />
      </Flex>
    );
  }

  if (error) {
    return (
      <Flex minH="100vh" align="center" justify="center">
        <Alert status="error">
          <AlertIcon />
          {error}
        </Alert>
      </Flex>
    );
  }

  if (!workspace) return null;

  return (
    <VStack spacing={0} align="stretch" minH="100vh">
      {/* Main Content */}
      <Flex flex={1}>
        {/* Show files loading or files sidebar */}
        {filesLoading ? (
          <Flex minH="100vh" align="center" justify="center" width="300px">
            <Spinner size="lg" color="blue.500" />
          </Flex>
        ) : files.length > 0 ? (
          <TablesSidebar 
            files={files} 
            selectedTableId={selectedTableId}
            onTableSelect={setSelectedTableId}
            onUploadClick={onOpen}
          />
        ) : null}

        {/* Main Content Area */}
        {filesLoading ? (
          <Flex flex={1} minH="100vh" align="center" justify="center">
            <Spinner size="xl" color="blue.500" />
          </Flex>
        ) : files.length === 0 ? (
          <NoFilesState onUploadClick={onOpen} />
        ) : selectedTableId ? (
          <TableDataView
            workspaceId={workspaceId || ''}
            tableId={selectedTableId}
            tableName={getSelectedTableName() || getSelectedFileName() || 'Unknown Table'}
          />
        ) : (
          <EmptyTableState onUploadClick={onOpen} />
        )}
      </Flex>

      {/* Upload Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Upload Files</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <FileUploader 
              workspaceId={workspaceId || ''} 
              onUploadComplete={handleUploadComplete}
            />
          </ModalBody>
        </ModalContent>
      </Modal>
    </VStack>
  );
};

export default WorkspacePage;
