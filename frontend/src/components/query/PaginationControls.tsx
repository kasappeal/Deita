import {
  Button,
  Flex,
  HStack,
  Icon,
  IconButton,
  Text,
  Tooltip
} from '@chakra-ui/react';
import React from 'react';
import { FiChevronLeft, FiChevronRight, FiChevronsLeft, FiChevronsRight, FiSave, FiShare } from 'react-icons/fi';

interface PaginationControlsProps {
  currentPage: number;
  hasMore: boolean;
  totalCount: number | null;
  loading: boolean;
  countLoading: boolean;
  exporting: boolean;
  saving: boolean;
  paginationMessage: string;
  onFirstPage: () => void;
  onPreviousPage: () => void;
  onNextPage: () => void;
  onLastPage: () => void;
  onSaveQuery: () => void;
  onExport: () => void;
  onFetchCount: () => void;
}

const PaginationControls: React.FC<PaginationControlsProps> = ({
  currentPage,
  hasMore,
  totalCount,
  loading,
  countLoading,
  exporting,
  saving,
  paginationMessage,
  onFirstPage,
  onPreviousPage,
  onNextPage,
  onLastPage,
  onSaveQuery,
  onExport,
  onFetchCount,
}) => {
  return (
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
            onClick={onSaveQuery}
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
            onClick={onExport}
            isLoading={exporting}
            icon={<Icon as={FiShare} />}
            isDisabled={loading || countLoading}
            variant="outline"
          />
        </Tooltip>
        <HStack spacing={2}>
          <Text fontSize="sm" color="gray.600">
            {paginationMessage}
          </Text>
          <Button
            size="sm"
            variant="outline"
            isLoading={countLoading}
            onClick={onFetchCount}
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
          onClick={onFirstPage}
        />
        <IconButton
          aria-label="Previous results"
          size="sm"
          variant="outline"
          icon={<Icon as={FiChevronLeft} />}
          isDisabled={currentPage === 1 || loading || countLoading}
          onClick={onPreviousPage}
        />
        <IconButton
          size="sm"
          aria-label="Next results"
          variant="outline"
          icon={<Icon as={FiChevronRight} />}
          isDisabled={!hasMore || loading || countLoading}
          onClick={onNextPage}
        />
        <IconButton
          size="sm"
          aria-label="Last results"
          variant="outline"
          icon={<Icon as={FiChevronsRight} />}
          isDisabled={!hasMore || loading || countLoading}
          onClick={onLastPage}
        />
      </HStack>
    </Flex>
  );
};

export default PaginationControls;
