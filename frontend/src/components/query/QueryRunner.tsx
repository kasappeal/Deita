import apiClient from '@/services/api';
import { Box, Button, Flex, Textarea, useToast } from '@chakra-ui/react';
import React, { useState } from 'react';

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

  const runQuery = async () => {
    if (!sqlQuery.trim() || !workspaceId) return;
    setQueryLoading(true);
    try {
      const res = await apiClient.post(`/v1/workspaces/${workspaceId}/query`, { query: sqlQuery });
      onResult?.(res.data);
      console.log('Query Result:', res.data);
    } catch (err) {
      onResult?.(null);
      console.error('Query Error:', err);
      toast({
        title: 'Query Error',
        description: 'Failed to execute query.',
        status: 'error',
        duration: 4000,
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
            placeholder="What do you want to know?"
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
            onKeyDown={e => {
              if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                // Run the query
                const form = e.currentTarget.form;
                if (form) {
                  form.requestSubmit();
                }
              }
            }}
          />
          <Button
            type="submit"
            colorScheme="blue"
            isLoading={queryLoading}
            isDisabled={!sqlQuery.trim() || queryLoading}
          >
            Run
          </Button>
        </Flex>
      </form>
    </Box>
  );
};

export default QueryRunner;
