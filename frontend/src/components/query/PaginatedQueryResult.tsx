import { workspaceApi } from '@/services/api';
import {
  Box,
  useToast,
} from '@chakra-ui/react';
import React, { useEffect, useState } from 'react';

import PaginationControls from './PaginationControls';
import QueryResultTable, { QueryResultData } from './QueryResultTable';
import SaveQueryModal from './SaveQueryModal';

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
  const [isSaveModalOpen, setIsSaveModalOpen] = useState(false);
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
    setIsSaveModalOpen(true);
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
      handleSaveModalClose();
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
    setIsSaveModalOpen(false);
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
      <PaginationControls
        currentPage={currentPage}
        hasMore={result.has_more}
        totalCount={totalCount}
        loading={loading}
        countLoading={countLoading}
        exporting={exporting}
        saving={saving}
        paginationMessage={getPaginationMessage()}
        onFirstPage={handleFirstPage}
        onPreviousPage={handlePreviousPage}
        onNextPage={handleNextPage}
        onLastPage={handleLastPage}
        onSaveQuery={handleSaveQuery}
        onExport={handleExport}
        onFetchCount={executeCountQuery}
      />

      {/* Query Results Table */}
      <Box flex={1} overflowY="auto">
        <QueryResultTable result={result} isLoading={exporting} />
      </Box>

      {/* Save Query Modal */}
      <SaveQueryModal
        isOpen={isSaveModalOpen}
        queryName={queryName}
        saving={saving}
        onClose={handleSaveModalClose}
        onQueryNameChange={setQueryName}
        onSave={handleSaveQueryConfirm}
      />
    </Box>
  );
};

export default PaginatedQueryResult;