import {
  Box,
  Button,
  Card,
  CardBody,
  Divider,
  Flex,
  Icon,
  IconButton,
  Stack,
  Text,
  Tooltip,
  VStack,
  useToast
} from '@chakra-ui/react';
import React, { useCallback, useEffect, useState } from 'react';
import { FiCode, FiDatabase, FiFile, FiFolder, FiLink, FiTrash2, FiUpload, FiZap } from 'react-icons/fi';
import { FileData, QueryData, workspaceApi } from '../../services/api';
import ChatInterface from './ChatInterface';

interface TableItem {
  id: string;
  name: string;
  fileName: string;
  rows: number;
  fileSize: string;
  isSelected?: boolean;
}

type TabType = 'tables' | 'sql' | 'ai';

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
  refreshQueries
}) => {
  const [activeTab, setActiveTab] = useState<TabType>('tables');
  const [savedQueries, setSavedQueries] = useState<QueryData[]>([]);
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

  const handleDeleteFile = async (fileId: string, fileName: string) => {
    if (window.confirm(`Are you sure you want to delete "${fileName}"? This action cannot be undone.`)) {
      try {
        if (workspaceId) {
          await workspaceApi.deleteFile(workspaceId, fileId);
        }
        onFileDelete?.(fileId);
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
      }
    }
  };

  const handleDeleteQuery = async (queryId: string, queryName: string) => {
    if (window.confirm(`Are you sure you want to delete the query "${queryName}"? This action cannot be undone.`)) {
      try {
        if (workspaceId) {
          await workspaceApi.deleteQuery(workspaceId, queryId);
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
      }
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

              return (
              <Card
                key={table.id}
                cursor="pointer"
                onClick={() => onTableSelect?.(table.id)}
                bg={isSelected ? "blue.50" : isInJoin ? "blue.50" : "white"}
                borderColor={isSelected ? "blue.200" : isInJoin ? "blue.200" : "gray.200"}
                borderWidth="1px"
                _hover={{
                  bg: isSelected ? "blue.50" : isInJoin ? "blue.50" : "gray.50",
                  borderColor: "blue.300"
                }}
                size="sm"
              >
                <CardBody p={3} position="relative">

                  {/* Link Button - Top Right */}
                  {selectedTableId && !isSelected && !isInJoin && (
                    <Tooltip label="Join with selected file" placement="top">
                      <IconButton
                        aria-label="Join files"
                        icon={<Icon as={FiLink} />}
                        size="xs"
                        variant="outline"
                        onClick={(e) => {
                          e.stopPropagation();
                          onJoinStart?.(selectedTableId!, table.id);
                        }}
                        position="absolute"
                        top={2}
                        right={2}
                        zIndex={2}
                      />
                    </Tooltip>
                  )}

                  {/* Add to Join Button - Top Right (when joining multiple tables) */}
                  {showAddToJoinButton && (
                    <Tooltip label="Add to join" placement="top">
                      <IconButton
                        aria-label="Add to join"
                        icon={<Icon as={FiLink} />}
                        size="xs"
                        variant="outline"
                        onClick={(e) => {
                          e.stopPropagation();
                          onJoinAdd?.(table.id);
                        }}
                        position="absolute"
                        top={2}
                        right={2}
                        zIndex={2}
                      />
                    </Tooltip>
                  )}

                  {/* Delete Button - Bottom Right */}
                  <Tooltip label="Delete file" placement="top">
                    <IconButton
                      aria-label="Delete file"
                      icon={<Icon as={FiTrash2} />}
                      size="xs"
                      variant="ghost"
                      colorScheme="red"
                      onClick={() => handleDeleteFile(table.id, table.fileName)}
                      position="absolute"
                      bottom={2}
                      right={2}
                      zIndex={1}
                    />
                  </Tooltip>

                  <VStack align="stretch" spacing={2}>
                    {/* Table Name */}
                    <Flex align="center" gap={2}>
                      <Text 
                        fontWeight="medium" 
                        color="gray.800" 
                        fontSize="sm"
                      >
                        {table.name}
                      </Text>
                      {isInJoin && (
                        <Icon 
                          as={FiLink} 
                          color="blue.500" 
                          boxSize={4}
                          opacity={0.7}
                        />
                      )}
                    </Flex>
                    
                    {/* File Source */}
                    <Flex align="center" gap={1}>
                      <Icon as={FiFile} color="gray.500" boxSize={3} />
                      <Text fontSize="xs" color="gray.500" noOfLines={1}>
                        {table.fileName}
                      </Text>
                    </Flex>
                    
                    {/* Stats Row */}
                    <Flex justify="space-between" fontSize="xs" color="gray.600">
                      <Flex align="center" gap={1}>
                        <Icon as={FiDatabase} boxSize={3} />
                        <Text>{table.rows.toLocaleString()} rows</Text>
                      </Flex>
                      <Text pr={8}>{table.fileSize}</Text>
                    </Flex>
                  </VStack>
                </CardBody>
              </Card>
              );
            })}
          </Stack>
        );
      case 'sql':
        return (
          <Stack spacing={2} flex={1}>
            {!savedQueries || savedQueries.length === 0 ? (
              <Box p={4} textAlign="center">
                <Text color="gray.500" fontSize="sm">No saved queries yet</Text>
              </Box>
            ) : (
              savedQueries.map((query) => (
                <Card
                  key={query.id}
                  cursor="pointer"
                  onClick={() => onQuerySelect?.(query)}
                  _hover={{ bg: "gray.50" }}
                  size="sm"
                >
                  <CardBody p={3} position="relative">

                    {/* Delete Button - Bottom Right */}
                    <Tooltip label="Delete query" placement="top">
                      <IconButton
                        aria-label="Delete query"
                        icon={<Icon as={FiTrash2} />}
                        size="xs"
                        variant="ghost"
                        colorScheme="red"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteQuery(query.id, query.name);
                        }}
                        position="absolute"
                        bottom={2}
                        right={2}
                        zIndex={1}
                      />
                    </Tooltip>

                    <VStack align="stretch" spacing={1}>
                      {/* Query Name */}
                      <Text 
                        fontWeight="medium" 
                        color="gray.800" 
                        fontSize="sm"
                      >
                        {query.name}
                      </Text>
                      
                      {/* Creation Date */}
                      <Text fontSize="xs" color="gray.500">
                        {new Date(query.created_at).toLocaleDateString()}
                      </Text>
                    </VStack>
                  </CardBody>
                </Card>
              ))
            )}
          </Stack>
        );
      case 'ai':
        return <ChatInterface />;
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
      p={4}
      overflow="hidden"
      display="flex"
      flexDirection="column"
      flexShrink={0}
    >
      <VStack align="stretch" spacing={2} flex={1} minH={0}>

        {/* Tab Buttons */}
        <Flex gap={1} justify="space-between" flexShrink={0}>
          <Tooltip label="Tables and files" placement="bottom">
            <IconButton
              aria-label="Tables and files"
              icon={<Icon as={FiFolder} />}
              size="sm"
              variant={activeTab === 'tables' ? 'solid' : 'ghost'}
              colorScheme={activeTab === 'tables' ? 'blue' : 'gray'}
              onClick={() => setActiveTab('tables')}
              flex={1}
            />
          </Tooltip>
          
          <Tooltip label="Saved queries" placement="bottom">
            <IconButton
              aria-label="Saved queries"
              icon={<Icon as={FiCode} />}
              size="sm"
              variant={activeTab === 'sql' ? 'solid' : 'ghost'}
              colorScheme={activeTab === 'sql' ? 'blue' : 'gray'}
              onClick={() => setActiveTab('sql')}
              flex={1}
            />
          </Tooltip>
          
          <Tooltip label="AI" placement="bottom">
            <IconButton
              aria-label="AI"
              icon={<Icon as={FiZap} />}
              size="sm"
              variant={activeTab === 'ai' ? 'solid' : 'ghost'}
              colorScheme={activeTab === 'ai' ? 'blue' : 'gray'}
              onClick={() => setActiveTab('ai')}
              flex={1}
            />
          </Tooltip>
        </Flex>

        {/* Separator */}
        <Divider flexShrink={0} />
        
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
    </Box>
  );
};

export default TablesSidebar;