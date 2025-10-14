import apiClient from '@/services/api';
import { Box, Button, Flex, Textarea, Tooltip, useToast } from '@chakra-ui/react';
import React, { useState } from 'react';
import { FaPlay } from 'react-icons/fa';

import { validateSqlSyntax } from '@/utils/sqlValidation';
import type { QueryResultData } from './QueryResultTable';

interface QueryRunnerProps {
  workspaceId: string;
  query?: string;
  setQuery?: (q: string) => void;
  runQuerySignal?: number;
  onResult?: (result: QueryResultData | null) => void;
}

const QueryRunner: React.FC<QueryRunnerProps> = ({ workspaceId, query, setQuery, runQuerySignal, onResult }) => {
  const [internalQuery, setInternalQuery] = useState('');
  const sqlQuery = query !== undefined ? query : internalQuery;
  const setSqlQuery = setQuery || setInternalQuery;
  const [queryLoading, setQueryLoading] = useState(false);
  const toast = useToast();

  // SQL validation
  const sqlValidation = validateSqlSyntax(sqlQuery);
  const isSqlValid = sqlValidation.isValid;

  const runQuery = async () => {
    if (!sqlQuery.trim() || !workspaceId || !isSqlValid) return;
    setQueryLoading(true);
    try {
      const res = await apiClient.post(`/v1/workspaces/${workspaceId}/query`, { query: sqlQuery });
      onResult?.(res.data);
    } catch (err) {
      onResult?.(null);
      console.error('Query Error:', err);
      const errorMessage = err instanceof Error && 'response' in err 
        ? (err as { response?: { data?: { error?: string } } }).response?.data?.error 
        : undefined;
      toast({
        title: 'Query Error',
        description: errorMessage?.replace(/\\x1b\[[0-9;]*m/g, '💥') || 'Failed to run query.',
        status: 'error',
        duration: 10000,
        isClosable: true,
      });
    } finally {
      setQueryLoading(false);
    }
  };

  // Run query when runQuerySignal changes (used for external trigger)
  React.useEffect(() => {
    if (runQuerySignal !== undefined) {
      runQuery();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [runQuerySignal]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    runQuery();
  };

  return (
    <Box p={4} borderBottom="1px" borderColor="gray.100" bg="gray.50">
      <form onSubmit={handleSubmit}>
        <Flex gap={2} align="center">
          <Textarea
            placeholder="Click in and join files or ask AI for your data"
            value={sqlQuery}
            onChange={e => setSqlQuery(e.target.value)}
            isDisabled={queryLoading}
            background={"white"}
            size="md"
            width="auto"
            flex={1}
            minH="40px"
            maxH="200px"
            resize="none"
            rows={sqlQuery.split('\n').length}
            borderColor={!isSqlValid && sqlQuery.trim() ? "red.300" : undefined}
            _hover={!isSqlValid && sqlQuery.trim() ? { borderColor: "red.400" } : undefined}
            onKeyDown={e => {
              if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                if (isSqlValid && sqlQuery.trim()) {
                  // Run the query
                  const form = e.currentTarget.form;
                  if (form) {
                    form.requestSubmit();
                  }
                }
              }
            }}
          />
          <Tooltip 
            label={
              !isSqlValid 
                ? sqlValidation.error || 'Invalid SQL syntax'
                : `Run Query (${navigator.platform.includes('Mac') ? 'Cmd' : 'Ctrl'}+Enter)`
            }
            placement="top"
            hasArrow
          >
            <Button
              type="submit"
              colorScheme="blue"
              isLoading={queryLoading}
              isDisabled={!sqlQuery.trim() || queryLoading || !isSqlValid}
              size="md"
              px={3}
            >
              <FaPlay />
            </Button>
          </Tooltip>
        </Flex>
      </form>
    </Box>
  );
};

export default QueryRunner;
