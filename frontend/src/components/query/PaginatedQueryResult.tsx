import { workspaceApi } from '@/services/api';
import {
  Box,
  Button,
  Flex,
  HStack,
  Icon,
  IconButton,
  Text,
  Tooltip,
  useToast,
} from '@chakra-ui/react';
import React, { useEffect, useState } from 'react';
import { FiChevronLeft, FiChevronRight, FiChevronsLeft, FiChevronsRight, FiSave, FiShare } from 'react-icons/fi';

import QueryResultTable, { QueryResultData } from './QueryResultTable';

interface PaginatedQueryResultProps {
  workspaceId: string;
  query: string;
  initialResult: QueryResultData;
  onQuerySaved?: () => void;
}

const PaginatedQueryResult: React.FC<PaginatedQueryResultProps> = ({
  workspaceId,
  query,
  initialResult,
  onQuerySaved,
}) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [result, setResult] = useState(initialResult);
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [totalCount, setTotalCount] = useState<number | null>(null);
  const [countLoading, setCountLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [resultsPerPage, setResultsPerPage] = useState<number | null>(null);
  const toast = useToast();

  // Update internal state when initialResult prop changes (e.g., when switching tables)
  useEffect(() => {
    setResult(initialResult);
    setCurrentPage(1); // Reset to first page when viewing new table
    setTotalCount(null); // Reset count when switching queries
    setResultsPerPage(null); // Reset results per page when switching queries
    
    // Store results per page from first request with has_more = true
    if (initialResult.has_more && initialResult.rows.length > 0) {
      setResultsPerPage(initialResult.rows.length);
    }
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
      
      // Store results per page from first request with has_more = true if we don't have it yet
      if (response.has_more && response.rows.length > 0 && resultsPerPage === null) {
        setResultsPerPage(response.rows.length);
      }
    } catch (error) {
      console.error('Query Error:', error);
      toast({
        title: 'Query Error',
        description: error.response?.data?.error || 'Failed to execute query.',
        status: 'error',
        duration: 10000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleFirstPage = () => {
    if (currentPage > 1) {
      executeQuery(1);
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

  const handleLastPage = async () => {
    if (!result.has_more) return;
    
    // If we don't know the total count, fetch it first
    if (totalCount === null) {
      setCountLoading(true);
      try {
        const response = await workspaceApi.executeQuery(workspaceId, query, 1, undefined, true);
        if (response.rows.length > 0 && response.rows[0].length > 0) {
          const count = response.rows[0][0] as number;
          setTotalCount(count);
          
          // Calculate and go to last page
          const pageSize = resultsPerPage || result.rows.length;
          const lastPage = Math.ceil(count / pageSize);
          executeQuery(lastPage);
        }
      } catch (error) {
        console.error('Count Query Error:', error);
        toast({
          title: 'Count Query Error',
          description: error.response?.data?.error || 'Failed to fetch total count.',
          status: 'error',
          duration: 4000,
          isClosable: true,
        });
      } finally {
        setCountLoading(false);
      }
    } else {
      // We have the count, calculate and go to last page
      const pageSize = resultsPerPage || result.rows.length;
      const lastPage = Math.ceil(totalCount / pageSize);
      executeQuery(lastPage);
    }
  };

  const handleSaveQuery = async () => {
    const queryName = prompt('Enter a name for this query:');
    if (!queryName || !queryName.trim()) {
      return;
    }

    setSaving(true);
    try {
      await workspaceApi.saveQuery(workspaceId, queryName.trim(), query);
      toast({
        title: 'Query Saved',
        description: `Query "${queryName}" has been saved successfully.`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      onQuerySaved?.();
    } catch (error) {
      console.error('Save Query Error:', error);
      toast({
        title: 'Save Query Error',
        description: 'Failed to save query.',
        status: 'error',
        duration: 4000,
        isClosable: true,
      });
    } finally {
      setSaving(false);
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
      const pageSize = resultsPerPage || rowCount;
      
      if (currentPage === 1 && !result.has_more) {
        // Single page with all results
        return `Showing 1 to ${rowCount} rows of`;
      } else if (currentPage === 1) {
        // First page with more results
        return `Showing 1 to ${rowCount} rows of`;
      } else {
        // Subsequent pages
        const startRow = (currentPage - 1) * pageSize + 1;
        const endRow = startRow + rowCount - 1;
        return `Showing ${startRow} to ${endRow} rows of`;
      }
    } else {
      // Fallback to original pagination messages when count is not available
      if (currentPage === 1) {
        return `Showing first ${rowCount} rows of`;
      } else if (result.has_more) {
        const pageSize = resultsPerPage || rowCount;
        const startRow = (currentPage - 1) * pageSize + 1;
        const endRow = startRow + rowCount - 1;
        return `Showing ${startRow} to ${endRow} rows of`;
      } else {
        return `Showing last ${rowCount} rows of`;
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
        {/* Left side: Save query, Export, and pagination message */}
        <HStack spacing={2}>
          <Tooltip label="Save Query" placement="bottom">
            <IconButton
              size="sm"
              aria-label="Save Query"
              onClick={handleSaveQuery}
              isLoading={saving}
              icon={<Icon as={FiSave} />}
              isDisabled={loading || countLoading}
              variant="outline"
            />
          </Tooltip>
          <Tooltip label="Export data to CSV" placement="bottom">
            <IconButton
              size="sm"
              aria-label="Export"
              onClick={handleExport}
              isLoading={exporting}
              icon={<Icon as={FiShare} />}
              isDisabled={loading || countLoading}
              variant="outline"
            />
          </Tooltip>
          <HStack spacing={2}>
            <Text fontSize="sm" color="gray.600">
              {getPaginationMessage()}
            </Text>
            <Button
              size="sm"
              variant="outline"
              isLoading={countLoading}
              onClick={executeCountQuery}
              isDisabled={loading}
            >
              {totalCount !== null ? totalCount.toLocaleString() : '?'}
            </Button>
          </HStack>
        </HStack>
        
        {/* Right side: Navigation buttons */}
        <HStack spacing={2}>
          <IconButton
            aria-label="Go to first results"
            size="sm"
            variant="outline"
            icon={<Icon as={FiChevronsLeft} />}
            isDisabled={currentPage === 1 || loading || countLoading}
            onClick={handleFirstPage}
          />
          <IconButton
            aria-label="Previous results"
            size="sm"
            variant="outline"
            icon={<Icon as={FiChevronLeft} />}
            isDisabled={currentPage === 1 || loading || countLoading}
            onClick={handlePreviousPage}
          />
          <IconButton
            size="sm"
            aria-label="Next results"
            variant="outline"
            icon={<Icon as={FiChevronRight} />}
            isDisabled={!result.has_more || loading || countLoading}
            onClick={handleNextPage}
          />
          <IconButton
            size="sm"
            aria-label="Last results"
            variant="outline"
            icon={<Icon as={FiChevronsRight} />}
            isDisabled={!result.has_more || loading || countLoading}
            onClick={handleLastPage}
          />
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