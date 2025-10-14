import { Box, Flex, Icon, Text } from '@chakra-ui/react';
import React from 'react';
import { FiCode, FiUser, FiZap } from 'react-icons/fi';

export interface UIMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  workspace_id: string;
  timestamp: Date;
  is_sql_query: boolean;
  message_metadata?: Record<string, unknown>;
}

interface MessageBubbleProps {
  message: UIMessage;
  onSqlClick?: (sqlQuery: string) => void;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, onSqlClick }) => {
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const renderSqlCard = () => {
    if (!message.is_sql_query || !message.message_metadata?.sql_query) return null;
    
    return (
      <Flex justify="flex-start" px={1} mt={2}>
        <Box
          maxWidth="85%"
          bg="blue.50"
          border="1px"
          borderColor="blue.200"
          borderRadius="md"
          overflow="hidden"
          cursor="pointer"
          _hover={{ bg: "blue.100", shadow: "md" }}
          onClick={() => {
            const sqlQuery = message.message_metadata?.sql_query as string;
            if (onSqlClick && sqlQuery) {
              onSqlClick(sqlQuery);
            }
          }}
        >
          <Box bg="blue.500" px={3} py={1}>
            <Flex align="center" gap={2}>
              <Icon as={FiCode} boxSize={3} color="white" />
              <Text fontSize="xs" color="white" fontWeight="medium">
                Click to see data
              </Text>
            </Flex>
          </Box>
          <Box px={3} py={2}>
            <Text
              fontSize="xs"
              fontFamily="mono"
              color="gray.700"
              whiteSpace="pre-wrap"
              maxH="50px"
              overflowY="auto"
            >
              {message.message_metadata.sql_query as string}
            </Text>
          </Box>
        </Box>
      </Flex>
    );
  };

  return (
    <Box mb={3}>
      {/* Regular message */}
      <Flex justify={message.role === 'user' ? 'flex-end' : 'flex-start'} px={1}>
        <Box
          maxWidth="85%"
          bg={message.role === 'user' ? 'blue.500' : 'white'}
          color={message.role === 'user' ? 'white' : 'gray.800'}
          px={3}
          py={2}
          borderRadius="md"
          boxShadow="sm"
          border={message.role === 'assistant' ? '1px' : 'none'}
          borderColor="gray.200"
        >
          <Flex align="center" gap={2} mb={1}>
            <Icon
              as={message.role === 'user' ? FiUser : FiZap}
              boxSize={3}
            />
            <Text fontSize="xs" opacity={0.8}>
              {message.role === 'user' ? 'You' : 'AI'}
            </Text>
            <Text fontSize="xs" opacity={0.6}>
              {formatTime(message.timestamp)}
            </Text>
          </Flex>
          <Text fontSize="sm" whiteSpace="pre-wrap">
            {message.content}
          </Text>
        </Box>
      </Flex>

      {/* SQL Query Card */}
      {renderSqlCard()}
    </Box>
  );
};

export default MessageBubble;
