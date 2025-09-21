import { workspaceApi } from '@/services/api';
import {
  Box,
  Button,
  Flex,
  HStack,
  Icon,
  Text,
  useToast,
} from '@chakra-ui/react';
import React, { useEffect, useState } from 'react';
import { FiChevronLeft, FiChevronRight } from 'react-icons/fi';

import QueryResultTable, { QueryResultData } from './QueryResultTable';

interface PaginatedQueryResultProps {
  workspaceId: string;
  query: string;
  initialResult: QueryResultData;
}

const PaginatedQueryResult: React.FC<PaginatedQueryResultProps> = ({
  workspaceId,
  query,
  initialResult,
}) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [result, setResult] = useState(initialResult);
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [totalCount, setTotalCount] = useState<number | null>(null);
  const [countLoading, setCountLoading] = useState(false);
  const toast = useToast();

  // Update internal state when initialResult prop changes (e.g., when switching tables)
  useEffect(() => {
    setResult(initialResult);
    setCurrentPage(1); // Reset to first page when viewing new table
    setTotalCount(null); // Reset count when switching queries
  }, [initialResult]);

  const executeCountQuery = async () => {
    setCountLoading(true);
    try {
      const response = await workspaceApi.executeQuery(workspaceId, query, 1, undefined, true);
      if (response.rows.length > 0 && response.rows[0].length > 0) {
        setTotalCount(response.rows[0][0] as number);
      }
    } catch (error) {
      console.error('Count Query Error:', error);
      toast({
        title: 'Count Query Error',
        description: 'Failed to fetch total count.',
        status: 'error',
        duration: 4000,
        isClosable: true,
      });
    } finally {
      setCountLoading(false);
    }
  };

  const executeQuery = async (page: number) => {
    setLoading(true);
    try {
      const response = await workspaceApi.executeQuery(workspaceId, query, page);
      setResult(response);
      setCurrentPage(page);
    } catch (error) {
      console.error('Query Error:', error);
      toast({
        title: 'Query Error',
        description: 'Failed to execute query.',
        status: 'error',
        duration: 4000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const handlePreviousPage = () => {
    if (currentPage > 1) {
      executeQuery(currentPage - 1);
    }
  };

  const handleNextPage = () => {
    if (result.has_more) {
      executeQuery(currentPage + 1);
    }
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const csvBlob = await workspaceApi.exportQueryAsCsv(workspaceId, query);
      
      // Create download link
      const url = window.URL.createObjectURL(csvBlob);
      const link = document.createElement('a');
      link.href = url;
      
      // Generate filename with timestamp
      const timestamp = new Date().toISOString().slice(0, 19).replace(/[T:]/g, '_');
      link.download = `query_export_${timestamp}.csv`;
      
      // Trigger download
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Clean up the URL object
      window.URL.revokeObjectURL(url);
      
      toast({
        title: 'Export Successful',
        description: 'Query results exported as CSV.',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Export Error:', error);
      toast({
        title: 'Export Error',
        description: 'Failed to export query results.',
        status: 'error',
        duration: 4000,
        isClosable: true,
      });
    } finally {
      setExporting(false);
    }
  };

  const getPaginationMessage = (): string => {
    const rowCount = result.rows.length;
    
    if (totalCount !== null) {
      // When we have total count, show more precise pagination info
      const formattedCount = totalCount.toLocaleString();
      
      if (currentPage === 1 && !result.has_more) {
        // Single page with all results
        return `Showing 1 to ${rowCount} of ${formattedCount}`;
      } else if (currentPage === 1) {
        // First page with more results
        return `Showing 1 to ${rowCount} of ${formattedCount}`;
      } else {
        // Subsequent pages
        const startRow = (currentPage - 1) * rowCount + 1;
        const endRow = startRow + rowCount - 1;
        return `Showing ${startRow} to ${endRow} of ${formattedCount}`;
      }
    } else {
      // Fallback to original pagination messages when count is not available
      if (currentPage === 1) {
        return `Showing first ${rowCount} rows`;
      } else if (result.has_more) {
        const startRow = (currentPage - 1) * rowCount + 1;
        const endRow = currentPage * rowCount;
        return `Showing rows ${startRow} to ${endRow}`;
      } else {
        return `Showing last ${rowCount} rows`;
      }
    }
  };

  return (
    <Box 
      width="100%" 
      height="100%"
      flex={1} 
      minWidth={0}
      display="flex" 
      flexDirection="column"
    >
      {/* Pagination Controls */}
      <Flex
        justify="space-between"
        align="center"
        mb={4}
        px={4}
        py={2}
        borderBottom="1px"
        borderColor="gray.200"
        bg="gray.50"
      >
        <HStack spacing={2}>
          <Button
            size="sm"
            variant="outline"
            leftIcon={<Icon as={FiChevronLeft} />}
            isDisabled={currentPage === 1 || loading}
            onClick={handlePreviousPage}
          />
          <Button
            size="sm"
            variant="outline"
            isLoading={countLoading}
            onClick={executeCountQuery}
            isDisabled={loading}
          >
            {totalCount !== null ? totalCount.toLocaleString() : '?'}
          </Button>
          <Button
            size="sm"
            variant="outline"
            rightIcon={<Icon as={FiChevronRight} />}
            isDisabled={!result.has_more || loading}
            onClick={handleNextPage}
          />
          <Text fontSize="sm" color="gray.600">
            {getPaginationMessage()}
          </Text>
        </HStack>
        
        <HStack>
          <Button
            size="sm"
            onClick={handleExport}
            isLoading={exporting}
            loadingText="Exporting..."
            isDisabled={loading}
          >
            Export
          </Button>
        </HStack>
      </Flex>

      {/* Query Results Table */}
      <Box flex={1} overflowY="auto">
        <QueryResultTable result={result} isLoading={exporting} />
      </Box>
    </Box>
  );
};

export default PaginatedQueryResult;