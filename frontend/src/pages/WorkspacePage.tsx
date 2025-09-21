
import FileUploader from '@/components/files/FileUploader';
import PaginatedQueryResult from '@/components/query/PaginatedQueryResult';
import { QueryResultData } from '@/components/query/QueryResultTable';
import QueryRunner from '@/components/query/QueryRunner';
import EmptyTableState, { NoFilesState } from '@/components/workspace/EmptyTableState';
import TablesSidebar from '@/components/workspace/TablesSidebar';
import { useAuth } from '@/contexts/AuthContext';
import apiClient, { FileData, workspaceApi } from '@/services/api';
import {
  Box,
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
import { useNavigate, useParams } from 'react-router-dom';

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
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [filesLoading, setFilesLoading] = useState(true);
  const [workspace, setWorkspaceLocal] = useState<Workspace | null>(null);
  const [files, setFiles] = useState<FileData[]>([]);
  const [selectedTableId, setSelectedTableId] = useState<string | undefined>();
  const [query, setQuery] = useState<string>('');
  const [executedQuery, setExecutedQuery] = useState<string>('');
  const [runQuerySignal, setRunQuerySignal] = useState<number>(0);
  const [queryResult, setQueryResult] = useState<QueryResultData | null>(null);
  const { setWorkspace } = useAuth();
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
      })
      .catch(() => {
        setWorkspaceLocal(null);
        setWorkspace(null);
        // Redirect to /workspaces when workspace doesn't exist
        navigate('/workspaces', { replace: true });
      })
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [workspaceId, navigate]);

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



  const handleQueryResult = (result: QueryResultData | null) => {
    setQueryResult(result);
    if (result !== null) {
      setExecutedQuery(query);
    }
  };

  // When a table is selected, write SELECT query and run it
  const handleTableSelect = (tableId: string) => {
    setSelectedTableId(tableId);
    const selectedFile = files.find(file => file.id === tableId);
    const tableName = selectedFile?.table_name || selectedFile?.filename?.replace(/\.[^/.]+$/, '') || 'unknown_table';
    setQuery(`SELECT * FROM "${tableName}"`);
    setRunQuerySignal(s => s + 1);
  };

  if (loading) {
    return (
      <Flex flex={1} align="center" justify="center">
        <Spinner size="xl" color="blue.500" />
      </Flex>
    );
  }

  if (!workspace) return null;

  return (
    <VStack spacing={0} align="stretch" flex={1} minH={0}>
      {/* Main Content */}
      <Flex flex={1} minH={0} align="stretch" maxH="calc(100vh - 80px)">
        {/* Show files loading or files sidebar */}
        {filesLoading ? (
          <Flex flex={1} align="center" justify="center" width="300px">
            <Spinner size="lg" color="blue.500" />
          </Flex>
        ) : files.length > 0 ? (
          <Box width="300px" flexShrink={0}>
            <TablesSidebar 
              files={files} 
              selectedTableId={selectedTableId}
              onTableSelect={handleTableSelect}
              onUploadClick={onOpen}
            />
          </Box>
        ) : null}

        {/* Main Content Area */}
        <Box flex={1} minW={0} display="flex" flexDirection="column" minH={0} overflow="hidden">
          {/* SQL Query Runner */}
          {workspaceId && files.length > 0 && (
            <QueryRunner 
              workspaceId={workspaceId} 
              query={query}
              setQuery={setQuery}
              runQuerySignal={runQuerySignal}
              onResult={handleQueryResult}
            />
          )}
          
          {filesLoading ? (
            <Flex flex={1} align="center" justify="center">
              <Spinner size="xl" color="blue.500" />
            </Flex>
          ) : files.length === 0 ? (
            <NoFilesState onUploadClick={onOpen} />
          ) : queryResult ? (
            <Box flex={1} minH={0} overflow="hidden">
              <PaginatedQueryResult 
                workspaceId={workspaceId!}
                query={executedQuery}
                initialResult={queryResult}
              />
            </Box>
          ) : (
            <EmptyTableState onUploadClick={onOpen} />
          )}
        </Box>
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
              existingFiles={files}
              onUploadComplete={handleUploadComplete}
            />
          </ModalBody>
        </ModalContent>
      </Modal>
    </VStack>
  );
};

export default WorkspacePage;
