import {
  Card,
  CardBody,
  Icon,
  IconButton,
  Text,
  Tooltip,
  VStack
} from '@chakra-ui/react';
import React from 'react';
import { FiTrash2 } from 'react-icons/fi';
import { QueryData } from '../../services/api';

interface SavedQueryCardProps {
  query: QueryData;
  onSelect: (query: QueryData) => void;
  onDelete: (queryId: string, queryName: string) => void;
}

const SavedQueryCard: React.FC<SavedQueryCardProps> = ({
  query,
  onSelect,
  onDelete,
}) => {
  return (
    <Card
      cursor="pointer"
      onClick={() => onSelect(query)}
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
              onDelete(query.id, query.name);
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
  );
};

export default SavedQueryCard;
