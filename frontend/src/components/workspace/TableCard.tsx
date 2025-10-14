import {
  Card,
  CardBody,
  Flex,
  Icon,
  IconButton,
  Text,
  Tooltip,
  VStack
} from '@chakra-ui/react';
import React from 'react';
import { FiDatabase, FiFile, FiLink, FiTrash2 } from 'react-icons/fi';

export interface TableItem {
  id: string;
  name: string;
  fileName: string;
  rows: number;
  fileSize: string;
  isSelected?: boolean;
}

interface TableCardProps {
  table: TableItem;
  isSelected: boolean;
  isInJoin: boolean;
  showLinkButton: boolean;
  showAddToJoinButton: boolean;
  onTableSelect: (tableId: string) => void;
  onJoinStart?: (tableId: string) => void;
  onJoinAdd?: (tableId: string) => void;
  onDelete: (fileId: string, fileName: string) => void;
  selectedTableId?: string;
}

const TableCard: React.FC<TableCardProps> = ({
  table,
  isSelected,
  isInJoin,
  showLinkButton,
  showAddToJoinButton,
  onTableSelect,
  onJoinStart,
  onJoinAdd,
  onDelete,
  selectedTableId,
}) => {
  return (
    <Card
      cursor="pointer"
      onClick={() => onTableSelect(table.id)}
      bg={isSelected ? "blue.50" : isInJoin ? "blue.50" : "white"}
      borderColor={isSelected ? "blue.200" : isInJoin ? "blue.200" : "gray.200"}
      borderWidth="1px"
      _hover={{
        bg: isSelected ? "blue.50" : isInJoin ? "blue.50" : "gray.50",
        borderColor: "blue.300"
      }}
      size="sm"
    >
      <CardBody p={3} position="relative">
        {/* Link Button - Top Right */}
        {showLinkButton && selectedTableId && (
          <Tooltip label="Join with selected file" placement="top">
            <IconButton
              aria-label="Join files"
              icon={<Icon as={FiLink} />}
              size="xs"
              variant="outline"
              onClick={(e) => {
                e.stopPropagation();
                onJoinStart?.(table.id);
              }}
              position="absolute"
              top={2}
              right={2}
              zIndex={2}
            />
          </Tooltip>
        )}

        {/* Add to Join Button - Top Right (when joining multiple tables) */}
        {showAddToJoinButton && (
          <Tooltip label="Add to join" placement="top">
            <IconButton
              aria-label="Add to join"
              icon={<Icon as={FiLink} />}
              size="xs"
              variant="outline"
              onClick={(e) => {
                e.stopPropagation();
                onJoinAdd?.(table.id);
              }}
              position="absolute"
              top={2}
              right={2}
              zIndex={2}
            />
          </Tooltip>
        )}

        {/* Delete Button - Bottom Right */}
        <Tooltip label="Delete file" placement="top">
          <IconButton
            aria-label="Delete file"
            icon={<Icon as={FiTrash2} />}
            size="xs"
            variant="ghost"
            colorScheme="red"
            onClick={(e) => {
              e.stopPropagation();
              onDelete(table.id, table.fileName);
            }}
            position="absolute"
            bottom={2}
            right={2}
            zIndex={1}
          />
        </Tooltip>

        <VStack align="stretch" spacing={2}>
          {/* Table Name */}
          <Flex align="center" gap={2}>
            <Text 
              fontWeight="medium" 
              color="gray.800" 
              fontSize="sm"
            >
              {table.name}
            </Text>
            {isInJoin && (
              <Icon 
                as={FiLink} 
                color="blue.500" 
                boxSize={4}
                opacity={0.7}
              />
            )}
          </Flex>
          
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
            <Text pr={8}>{table.fileSize}</Text>
          </Flex>
        </VStack>
      </CardBody>
    </Card>
  );
};

export default TableCard;
