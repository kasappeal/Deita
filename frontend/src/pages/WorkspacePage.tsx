import FileUploader from '@/components/files/FileUploader';
import PaginatedQueryResult from '@/components/query/PaginatedQueryResult';
import { QueryResultData } from '@/components/query/QueryResultTable';
import QueryRunner from '@/components/query/QueryRunner';
import EmptyTableState, { NoFilesState } from '@/components/workspace/EmptyTableState';
import JoinModal from '@/components/workspace/JoinModal';
import JoinedTableSelectionModal from '@/components/workspace/JoinedTableSelectionModal';
import TableSelectionModal from '@/components/workspace/TableSelectionModal';
import TablesSidebar from '@/components/workspace/TablesSidebar';
import { useAuth } from '@/contexts/AuthContext';
import { useJoinTables } from '@/hooks/useJoinTables';
import apiClient, { FileData, QueryData, workspaceApi } from '@/services/api';
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
import React, { useEffect, useRef, useState } from 'react';
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
  const [isJoinGeneratedQuery, setIsJoinGeneratedQuery] = useState<boolean>(false);
  const lastProgrammaticQueryRef = useRef<string>('');
  const [queryResult, setQueryResult] = useState<QueryResultData | null>(null);
  const { setWorkspace } = useAuth();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [autoOpenUpload, setAutoOpenUpload] = useState(false);
  const [pendingNewTableId, setPendingNewTableId] = useState<string | null>(null);
  const [refreshQueriesSignal, setRefreshQueriesSignal] = useState<number>(0);
  const toast = useToast();

  const {
    joinState,
    isJoinModalOpen,
    isTableSelectionModalOpen,
    isJoinedTableSelectionModalOpen,
    startJoinWithTwoTables,
    addTableToJoin,
    addJoinCondition,
    startJoinWithJoinedTable,
    resetJoin,
    setIsJoinModalOpen,
    setIsTableSelectionModalOpen,
    setIsJoinedTableSelectionModalOpen,
  } = useJoinTables();


  // Fetch workspace data
  useEffect(() => {
    if (!workspaceId) return;
    
    setLoading(true);
    apiClient.get(`/v1/workspaces/${workspaceId}`)
      .then(res => {
        setWorkspaceLocal(res.data);
        setWorkspace(res.data);
        // Store as last visited workspace
        localStorage.setItem('lastVisitedWorkspaceId', res.data.id);
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

  const handleFileDelete = (fileId: string) => {
    // Remove the deleted file from the state and refresh files
    setFiles(prevFiles => prevFiles.filter(file => file.id !== fileId));
    
    // If the deleted file was selected, clear the selection
    if (selectedTableId === fileId) {
      setSelectedTableId(undefined);
      setQuery('');
      setQueryResult(null);
      setExecutedQuery('');
    }
  };



  const handleQueryResult = (result: QueryResultData | null) => {
    setQueryResult(result);
    if (result !== null) {
      setExecutedQuery(query);
      
      // If a non-join-generated query was executed successfully, clear joins
      if (!isJoinGeneratedQuery) {
        resetJoin();
      }
    }
  };

  // When a table is selected, write SELECT query and run it
  const handleTableSelect = (tableId: string) => {
    // Clear any existing joins when selecting a table
    resetJoin();
    
    setSelectedTableId(tableId);
    const selectedFile = files.find(file => file.id === tableId);
    const tableName = selectedFile?.table_name || selectedFile?.filename?.replace(/\.[^/.]+$/, '') || 'unknown_table';
    const newQuery = `SELECT * FROM "${tableName}"`;
    setQuery(newQuery);
    lastProgrammaticQueryRef.current = newQuery;
    setIsJoinGeneratedQuery(false); // This is a simple table selection query, not join-generated
    setRunQuerySignal(s => s + 1);
  };

  const handleQuerySelect = (selectedQuery: QueryData) => {
    setQuery(selectedQuery.query);
    setRunQuerySignal(s => s + 1);
  };

  const handleSqlQueryFromChat = (sqlQuery: string) => {
    setQuery(sqlQuery);
    setRunQuerySignal(s => s + 1);
  };

  const handleJoinStart = (leftTableId: string, rightTableId: string) => {
    startJoinWithTwoTables(leftTableId, rightTableId);
  };

  const handleClearJoins = () => {
    resetJoin();
    setSelectedTableId(undefined);
    setQuery('');
    setQueryResult(null);
    setExecutedQuery('');
    setIsJoinGeneratedQuery(false);
    lastProgrammaticQueryRef.current = '';
  };

  const handleJoinAdd = (tableId: string) => {
    // If there are already joined tables, ask which one to connect to
    if (joinState.selectedTables.length > 1) {
      setPendingNewTableId(tableId);
      setIsJoinedTableSelectionModalOpen(true);
    } else {
      // Normal flow for first join
      addTableToJoin(tableId, files);
    }
  };

  const handleSelectJoinedTable = (joinedTableId: string) => {
    if (pendingNewTableId) {
      startJoinWithJoinedTable(joinedTableId, pendingNewTableId, files);
      setPendingNewTableId(null);
    }
  };

  const handleJoinCondition = (leftTable: string, rightTable: string, leftField: string, rightField: string, joinType: 'INNER' | 'LEFT' | 'RIGHT' | 'FULL') => {
    // First add the join condition
    addJoinCondition(leftTable, rightTable, leftField, rightField, joinType);
    
    // Calculate what the new join state will be after adding the condition
    const newJoinConditions = [...joinState.joinConditions, { leftTable, rightTable, leftField, rightField, joinType }];
    const newSelectedTables = [...joinState.selectedTables];
    
    // If the right table is not already in selected tables, add it
    if (!newSelectedTables.includes(rightTable)) {
      newSelectedTables.push(rightTable);
    }
    
    // Generate the query based on the new state
    const tableNames = newSelectedTables.map(tableId => {
      const file = files.find(f => f.id === tableId);
      return file?.table_name || file?.filename?.replace(/\.[^/.]+$/, '') || 'unknown_table';
    });

    // Create a mapping from table ID to table name for easier lookup
    const tableIdToName: Record<string, string> = {};
    newSelectedTables.forEach((tableId, index) => {
      tableIdToName[tableId] = tableNames[index];
    });

    let joinQuery = `SELECT *\nFROM "${tableNames[0]}"`;
    for (let i = 1; i < tableNames.length; i++) {
      const condition = newJoinConditions[i - 1];
      if (condition) {
        const leftTableName = tableIdToName[condition.leftTable];
        const rightTableName = tableIdToName[condition.rightTable];
        joinQuery += `\n${condition.joinType} JOIN "${rightTableName}" ON "${leftTableName}"."${condition.leftField}" = "${rightTableName}"."${condition.rightField}"`;
      }
    }
    
    // Set the query and execute it
    setQuery(joinQuery);
    lastProgrammaticQueryRef.current = joinQuery;
    setIsJoinGeneratedQuery(true); // This query was generated by the join mechanism
    setRunQuerySignal(s => s + 1);
  };

  // Watch for query changes to detect manual edits
  useEffect(() => {
    if (query !== lastProgrammaticQueryRef.current && lastProgrammaticQueryRef.current !== '') {
      // User has modified the query manually
      setIsJoinGeneratedQuery(false);
    }
  }, [query]);

  const handleQuerySaved = () => {
    setRefreshQueriesSignal(prev => prev + 1);
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
              onFileDelete={handleFileDelete}
              workspaceId={workspaceId}
              onJoinStart={handleJoinStart}
              onJoinAdd={handleJoinAdd}
              joinState={joinState}
              onClearJoins={handleClearJoins}
              onQuerySelect={handleQuerySelect}
              refreshQueries={refreshQueriesSignal}
              onSqlQuery={handleSqlQueryFromChat}
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
                onQuerySaved={handleQuerySaved}
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

      {/* Join Modal */}
      <JoinModal
        isOpen={isJoinModalOpen}
        onClose={() => {
          setIsJoinModalOpen(false);
          resetJoin(); // Reset join state when modal is closed
        }}
        leftTableId={joinState.currentJoinTable || ''}
        rightTableId={joinState.selectedTables[joinState.selectedTables.length - 1] || ''}
        files={files}
        onJoin={handleJoinCondition}
      />

      {/* Table Selection Modal */}
      <TableSelectionModal
        isOpen={isTableSelectionModalOpen}
        onClose={() => setIsTableSelectionModalOpen(false)}
        availableTables={files.filter(f => !joinState.selectedTables.includes(f.id))}
        onTableSelect={handleJoinAdd}
      />

      {/* Joined Table Selection Modal - New */}
      <JoinedTableSelectionModal
        isOpen={isJoinedTableSelectionModalOpen}
        onClose={() => setIsJoinedTableSelectionModalOpen(false)}
        joinedTableIds={joinState.selectedTables}
        newTableId={pendingNewTableId || ''}
        files={files}
        onSelectJoinedTable={handleSelectJoinedTable}
      />
    </VStack>
  );
};

export default WorkspacePage;
