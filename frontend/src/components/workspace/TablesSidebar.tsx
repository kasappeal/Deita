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
  VStack
} from '@chakra-ui/react';
import React, { useState } from 'react';
import { FiCode, FiDatabase, FiFile, FiFolder, FiUpload, FiZap } from 'react-icons/fi';
import { FileData } from '../../services/api';
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
  return filename.replace(/\.[^/.]+$/, "").replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

const TablesSidebar: React.FC<TablesSidebarProps> = ({ 
  files, 
  selectedTableId, 
  onTableSelect,
  onUploadClick 
}) => {
  const [activeTab, setActiveTab] = useState<TabType>('tables');

  const tables: TableItem[] = files.map(file => ({
    id: file.id,
    name: getTableDisplayName(file.filename),
    fileName: file.filename,
    rows: typeof file.csv_metadata?.rows === 'number' ? file.csv_metadata.rows 
          : typeof file.csv_metadata?.row_count === 'number' ? file.csv_metadata.row_count 
          : 0,
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

            {tables.map((table) => (
              <Card
                key={table.id}
                cursor="pointer"
                onClick={() => onTableSelect?.(table.id)}
                bg={selectedTableId === table.id ? "blue.50" : "white"}
                borderColor={selectedTableId === table.id ? "blue.200" : "gray.200"}
                borderWidth="1px"
                _hover={{
                  bg: selectedTableId === table.id ? "blue.50" : "gray.50",
                  borderColor: "blue.300"
                }}
                size="sm"
              >
                <CardBody p={3}>
                  <VStack align="stretch" spacing={2}>
                    {/* Table Name */}
                    <Text fontWeight="medium" color="gray.800" fontSize="sm">
                      {table.name}
                    </Text>
                    
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
                      <Text>{table.fileSize}</Text>
                    </Flex>
                  </VStack>
                </CardBody>
              </Card>
            ))}
          </Stack>
        );
      case 'sql':
        return (
          <Box flex={1} p={4} textAlign="center">
            <Text color="gray.500" fontSize="sm">SQL tools coming soon...</Text>
          </Box>
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
          
          <Tooltip label="SQL" placement="bottom">
            <IconButton
              aria-label="SQL"
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