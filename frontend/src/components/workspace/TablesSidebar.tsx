import {
    Box,
    Button,
    Card,
    CardBody,
    Flex,
    Icon,
    Stack,
    Text,
    VStack
} from '@chakra-ui/react';
import React from 'react';
import { FiDatabase, FiFile, FiPlus } from 'react-icons/fi';
import { FileData } from '../../services/api';

interface TableItem {
  id: string;
  name: string;
  fileName: string;
  rows: number;
  fileSize: string;
  isSelected?: boolean;
}

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
  const tables: TableItem[] = files.map(file => ({
    id: file.id,
    name: getTableDisplayName(file.filename),
    fileName: file.filename,
    rows: typeof file.csv_metadata?.rows === 'number' ? file.csv_metadata.rows 
          : typeof file.csv_metadata?.row_count === 'number' ? file.csv_metadata.row_count 
          : 0,
    fileSize: formatFileSize(file.size),
  }));

  return (
    <Box
      width="300px"
      minWidth="300px"
      minH="100%"
      bg="gray.50"
      borderRight="1px"
      borderColor="gray.200"
      p={4}
      overflow="auto"
      display="flex"
      flexDirection="column"
      flexShrink={0}
    >
      <VStack align="stretch" spacing={2} flex={1}>
        <Button
            colorScheme="blue"
            variant="outline"
            leftIcon={<Icon as={FiPlus} />}
            onClick={onUploadClick}
            size="sm"
            width="full"
            >
            Upload Files
        </Button>

        {/* Tables List */}
        <Stack spacing={2} flex={1}>
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

      </VStack>
    </Box>
  );
};

export default TablesSidebar;