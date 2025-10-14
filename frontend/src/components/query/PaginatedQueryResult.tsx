import { workspaceApi } from '@/services/api';
import {
  Box,
  Button,
  Flex,
  FormControl,
  FormLabel,
  HStack,
  Icon,
  IconButton,
  Input,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
  Text,
  Tooltip,
  useDisclosure,
  useToast,
} from '@chakra-ui/react';
import React, { useEffect, useRef, useState } from 'react';
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
  const [queryName, setQueryName] = useState('');
  const { isOpen: isSaveModalOpen, onOpen: onSaveModalOpen, onClose: onSaveModalClose } = useDisclosure();
  const toast = useToast();
  const initialFocusRef = useRef<HTMLInputElement>(null);

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
      const errorMessage = error instanceof Error && 'response' in error 
        ? (error as { response?: { data?: { error?: string } } }).response?.data?.error 
        : undefined;
      toast({
        title: 'Query Error',
        description: errorMessage || 'Failed to execute query.',
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
        const errorMessage = error instanceof Error && 'response' in error 
          ? (error as { response?: { data?: { error?: string } } }).response?.data?.error 
          : undefined;
        toast({
          title: 'Count Query Error',
          description: errorMessage || 'Failed to fetch total count.',
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

  const handleSaveQuery = () => {
    setQueryName('');
    onSaveModalOpen();
  };

  const handleSaveQueryConfirm = async () => {
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
      onSaveModalClose();
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

  const handleSaveModalClose = () => {
    setQueryName('');
    onSaveModalClose();
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
      const formattedTotal = totalCount.toLocaleString();
      
      if (currentPage === 1 && !result.has_more) {
        // Single page with all results
        return `Showing 1 to ${rowCount} of ${formattedTotal}`;
      } else if (currentPage === 1) {
        // First page with more results
        return `Showing 1 to ${rowCount} of ${formattedTotal}`;
      } else {
        // Subsequent pages
        const startRow = (currentPage - 1) * pageSize + 1;
        const endRow = startRow + rowCount - 1;
        return `Showing ${startRow} to ${endRow} of ${formattedTotal}`;
      }
    } else {
      // Fallback to pagination messages when count is not available
      if (currentPage === 1) {
        return `Showing first ${rowCount} rows of`;
      } else if (result.has_more) {
        // Middle pages - calculate based on results per page
        const pageSize = resultsPerPage || rowCount;
        const startRow = (currentPage - 1) * pageSize + 1;
        const endRow = startRow + rowCount - 1;
        return `Showing rows ${startRow} to ${endRow}`;
      } else {
        // Last page
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
        {/* Left side: Save query, Export, and pagination message */}
        <HStack spacing={2}>
          <Tooltip label="Save Query" placement="bottom" openDelay={500} hasArrow>
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
          <Tooltip label="Export to CSV" placement="bottom" openDelay={500} hasArrow>
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
            <Tooltip label="Count number of rows" placement="bottom" openDelay={500} hasArrow>
              <Button
                size="sm"
                variant="outline"
                isLoading={countLoading}
                onClick={executeCountQuery}
                isDisabled={loading || totalCount !== null}
              >
                {totalCount !== null ? totalCount.toLocaleString() : '?'}
              </Button>
            </Tooltip>
          </HStack>
        </HStack>
        
        {/* Right side: Navigation buttons */}
        <HStack spacing={2}>
          <Tooltip label="Go to first results" placement="bottom" openDelay={500} hasArrow>
            <IconButton
              aria-label="Go to first results"
              size="sm"
              variant="outline"
              icon={<Icon as={FiChevronsLeft} />}
              isDisabled={currentPage === 1 || loading || countLoading}
              onClick={handleFirstPage}
            />
          </Tooltip>
          <Tooltip label="Previous results" placement="bottom" openDelay={500} hasArrow>
            <IconButton
              aria-label="Previous results"
              size="sm"
              variant="outline"
              icon={<Icon as={FiChevronLeft} />}
              isDisabled={currentPage === 1 || loading || countLoading}
              onClick={handlePreviousPage}
            />
          </Tooltip>
          <Tooltip label="Next results" placement="bottom" openDelay={500} hasArrow>
            <IconButton
              size="sm"
              aria-label="Next results"
              variant="outline"
              icon={<Icon as={FiChevronRight} />}
              isDisabled={!result.has_more || loading || countLoading}
              onClick={handleNextPage}
            />
          </Tooltip>
          <Tooltip label="Last results" placement="bottom" openDelay={500} hasArrow>
            <IconButton
              size="sm"
              aria-label="Last results"
              variant="outline"
              icon={<Icon as={FiChevronsRight} />}
              isDisabled={!result.has_more || loading || countLoading}
              onClick={handleLastPage}
            />
          </Tooltip>
        </HStack>
      </Flex>

      {/* Query Results Table */}
      <Box flex={1} overflowY="auto">
        <QueryResultTable result={result} isLoading={exporting} />
      </Box>

      {/* Save Query Modal */}
      <Modal isOpen={isSaveModalOpen} onClose={handleSaveModalClose} isCentered initialFocusRef={initialFocusRef}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Save Query</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <FormControl>
              <FormLabel>Query Name</FormLabel>
              <Input
                ref={initialFocusRef}
                placeholder="Enter a name for this query"
                value={queryName}
                onChange={(e) => setQueryName(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && queryName.trim()) {
                    handleSaveQueryConfirm();
                  }
                }}
              />
            </FormControl>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={handleSaveModalClose}>
              Cancel
            </Button>
            <Button
              colorScheme="blue"
              onClick={handleSaveQueryConfirm}
              isLoading={saving}
              isDisabled={!queryName.trim()}
            >
              Save Query
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default PaginatedQueryResult;