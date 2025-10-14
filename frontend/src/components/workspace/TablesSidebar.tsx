import {
  Box,
  Button,
  Divider,
  Icon,
  Stack,
  Text,
  VStack,
  useToast
} from '@chakra-ui/react';
import React, { useCallback, useEffect, useState } from 'react';
import { FiTrash2, FiUpload } from 'react-icons/fi';
import { FileData, QueryData, workspaceApi } from '../../services/api';
import ChatInterface from './ChatInterface';
import DeleteConfirmationDialog from './DeleteConfirmationDialog';
import SavedQueryCard from './SavedQueryCard';
import TabButtons, { TabType } from './TabButtons';
import TableCard, { TableItem } from './TableCard';

interface TablesSidebarProps {
  files: FileData[];
  selectedTableId?: string;
  onTableSelect?: (tableId: string) => void;
  onUploadClick?: () => void;
  onFileDelete?: (fileId: string) => void;
  workspaceId?: string;
  onJoinStart?: (leftTableId: string, rightTableId: string) => void;
  onJoinAdd?: (tableId: string) => void;
  joinState?: { selectedTables: string[]; joinConditions: { leftTable: string; rightTable: string; leftField: string; rightField: string }[] };
  onClearJoins?: () => void;
  onQuerySelect?: (query: QueryData) => void;
  refreshQueries?: number; // Signal to refresh saved queries
  onSqlQuery?: (sqlQuery: string) => void;
}

// Helper function to format file size
const formatFileSize = (bytes: number): string => {
  const sizes = ['B', 'KB', 'MB', 'GB'];
  if (bytes === 0) return '0 B';
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
};

// Helper function to format table name from filename
const getTableDisplayName = (filename: string): string => {
  return filename.replace(/\.[^/.]+$/, "").replace(/_/g, ' ');
};

const TablesSidebar: React.FC<TablesSidebarProps> = ({ 
  files, 
  selectedTableId, 
  onTableSelect,
  onUploadClick,
  onFileDelete,
  workspaceId,
  onJoinStart,
  onJoinAdd,
  joinState,
  onClearJoins,
  onQuerySelect,
  refreshQueries,
  onSqlQuery
}) => {
  const [activeTab, setActiveTab] = useState<TabType>('tables');
  const [savedQueries, setSavedQueries] = useState<QueryData[]>([]);
  const [deleteConfirmation, setDeleteConfirmation] = useState<{
    isOpen: boolean;
    type: 'file' | 'query';
    id: string;
    name: string;
  }>({
    isOpen: false,
    type: 'file',
    id: '',
    name: ''
  });
  const toast = useToast();

  const fetchSavedQueries = useCallback(async () => {
    try {
      const response = await workspaceApi.getQueries(workspaceId!);
      setSavedQueries(response);
    } catch (error) {
      console.error('Error fetching saved queries:', error);
      toast({
        title: 'Error loading saved queries',
        description: 'Please try again later',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  }, [workspaceId, toast]);

  useEffect(() => {
    if (workspaceId && activeTab === 'sql') {
      fetchSavedQueries();
    }
  }, [workspaceId, activeTab, fetchSavedQueries]);

  useEffect(() => {
    if (refreshQueries !== undefined && activeTab === 'sql') {
      fetchSavedQueries();
    }
  }, [refreshQueries, activeTab, fetchSavedQueries]);

  const handleDeleteFile = (fileId: string, fileName: string) => {
    setDeleteConfirmation({
      isOpen: true,
      type: 'file',
      id: fileId,
      name: fileName
    });
  };

  const confirmDeleteFile = async () => {
    try {
      if (workspaceId) {
        await workspaceApi.deleteFile(workspaceId, deleteConfirmation.id);
      }
      onFileDelete?.(deleteConfirmation.id);
      toast({
        title: 'File deleted successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: 'Error deleting file',
        description: 'Please try again later',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      console.error('Error deleting file:', error);
    } finally {
      setDeleteConfirmation({ isOpen: false, type: 'file', id: '', name: '' });
    }
  };

  const handleDeleteQuery = (queryId: string, queryName: string) => {
    setDeleteConfirmation({
      isOpen: true,
      type: 'query',
      id: queryId,
      name: queryName
    });
  };

  const confirmDeleteQuery = async () => {
    try {
      if (workspaceId) {
        await workspaceApi.deleteQuery(workspaceId, deleteConfirmation.id);
      }
      // Reload queries after deletion
      fetchSavedQueries();
      toast({
        title: 'Query deleted successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: 'Error deleting query',
        description: 'Please try again later',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      console.error('Error deleting query:', error);
    } finally {
      setDeleteConfirmation({ isOpen: false, type: 'query', id: '', name: '' });
    }
  };

  const closeDeleteConfirmation = () => {
    setDeleteConfirmation({ isOpen: false, type: 'file', id: '', name: '' });
  };

  const handleConfirmDelete = () => {
    if (deleteConfirmation.type === 'file') {
      confirmDeleteFile();
    } else {
      confirmDeleteQuery();
    }
  };

  const tables: TableItem[] = files.map(file => ({
    id: file.id,
    name: getTableDisplayName(file.filename),
    fileName: file.filename,
    rows: file.row_count || 0,
    fileSize: formatFileSize(file.size),
  }));

  const renderTabContent = () => {
    switch (activeTab) {
      case 'tables':
        return (
          <Box p={2}>
            <Stack spacing={2} flex={1}>
              <Button
                colorScheme="blue"
                variant="outline"
                leftIcon={<Icon as={FiUpload} />}
                onClick={onUploadClick}
                size="sm"
                width="full"
              >
                Upload Files
              </Button>

              {joinState && joinState.selectedTables.length > 0 && (
                <Button
                  colorScheme="red"
                  variant="outline"
                  leftIcon={<Icon as={FiTrash2} />}
                  onClick={onClearJoins}
                  size="sm"
                  width="full"
                >
                  Clear Joins
                </Button>
              )}

              {tables.map((table) => {
                const isSelected = selectedTableId === table.id;
                const isInJoin = joinState?.selectedTables.includes(table.id);
                const showAddToJoinButton = joinState && joinState.selectedTables.length > 0 && !isInJoin;
                const showLinkButton = selectedTableId && !isSelected && !isInJoin;

                return (
                  <TableCard
                    key={table.id}
                    table={table}
                    isSelected={!!isSelected}
                    isInJoin={!!isInJoin}
                    showLinkButton={!!showLinkButton}
                    showAddToJoinButton={!!showAddToJoinButton}
                    onTableSelect={onTableSelect || (() => {})}
                    onJoinStart={(tableId) => onJoinStart?.(selectedTableId!, tableId)}
                    onJoinAdd={onJoinAdd}
                    onDelete={handleDeleteFile}
                    selectedTableId={selectedTableId}
                  />
                );
              })}
            </Stack>
          </Box>
        );
      case 'sql':
        return (
          <Box p={2}>
            <Stack spacing={2} flex={1}>
              {!savedQueries || savedQueries.length === 0 ? (
                <Box p={4} textAlign="center">
                  <Text color="gray.500" fontSize="sm">No saved queries yet</Text>
                </Box>
              ) : (
                savedQueries.map((query) => (
                  <SavedQueryCard
                    key={query.id}
                    query={query}
                    onSelect={onQuerySelect || (() => {})}
                    onDelete={handleDeleteQuery}
                  />
                ))
              )}
            </Stack>
          </Box>
        );
      case 'ai':
        return <ChatInterface workspaceId={workspaceId} onSqlQuery={onSqlQuery} />;
      default:
        return null;
    }
  };

  return (
    <Box
      width="300px"
      minWidth="300px"
      height="calc(100vh - 80px)"
      maxHeight="calc(100vh - 80px)"
      bg="gray.50"
      borderRight="1px"
      borderColor="gray.200"
      p={0}
      overflow="hidden"
      display="flex"
      flexDirection="column"
      flexShrink={0}
    >
      <VStack align="stretch" spacing={2} flex={1} minH={0}>

        {/* Tab Buttons */}
        <TabButtons activeTab={activeTab} onTabChange={setActiveTab} />

        {/* Separator */}
        <Divider flexShrink={0} m={0} />
        
        {/* Tab Content */}
        <Box 
          flex={1} 
          overflow={activeTab === 'ai' ? 'hidden' : 'auto'} 
          minH={0}
          display="flex"
          flexDirection="column"
        >
          {renderTabContent()}
        </Box>

      </VStack>

      {/* Delete Confirmation Modal */}
      <DeleteConfirmationDialog
        isOpen={deleteConfirmation.isOpen}
        itemType={deleteConfirmation.type}
        itemName={deleteConfirmation.name}
        onClose={closeDeleteConfirmation}
        onConfirm={handleConfirmDelete}
      />
    </Box>
  );
};

export default TablesSidebar;