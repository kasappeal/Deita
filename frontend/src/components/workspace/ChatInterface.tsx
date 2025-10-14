import {
  Box,
  Flex,
  Icon,
  IconButton,
  Spinner,
  Text,
  Textarea,
  Tooltip,
  VStack,
  useToast
} from '@chakra-ui/react';
import React, { useEffect, useRef, useState } from 'react';
import { FiCode, FiSend, FiTrash2, FiUser, FiZap } from 'react-icons/fi';
import { ChatMessage, workspaceApi } from '../../services/api';

interface ChatInterfaceProps {
  workspaceId?: string;
  onQuery?: (query: string) => Promise<unknown>;
  onSqlQuery?: (sqlQuery: string) => void;
}

// Local message interface for UI (extends ChatMessage with timestamp as Date)
interface UIMessage extends Omit<ChatMessage, 'created_at'> {
  timestamp: Date;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ workspaceId, onQuery, onSqlQuery }) => {
  const [messages, setMessages] = useState<UIMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const isLoadingHistoryRef = useRef(false);
  const toast = useToast();

  const scrollToBottom = () => {
    if (messagesEndRef.current && typeof messagesEndRef.current.scrollIntoView === 'function') {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  // Convert ChatMessage to UIMessage
  const convertToUIMessage = (chatMessage: ChatMessage): UIMessage => ({
    ...chatMessage,
    timestamp: new Date(chatMessage.created_at),
  });

  // Load chat history on mount
  useEffect(() => {
    let isMounted = true;
    
    const loadChatHistory = async () => {
      if (!workspaceId) return;
      
      // Avoid duplicate calls but ensure we can always load initially
      if (isLoadingHistoryRef.current) return;
      
      isLoadingHistoryRef.current = true;
      setIsLoadingHistory(true);
      
      try {
        const chatMessages = await workspaceApi.getChatMessages(workspaceId);
        
        // Only update state if component is still mounted
        if (isMounted) {
          const uiMessages = chatMessages.map(convertToUIMessage);
          setMessages(uiMessages);
        }
      } catch (error) {
        if (isMounted) {
          console.error('Failed to load chat history:', error);
          toast({
            title: 'Warning',
            description: 'Failed to load chat history',
            status: 'warning',
            duration: 3000,
            isClosable: true,
          });
        }
      } finally {
        // Always clear loading state and ref, regardless of mount status
        isLoadingHistoryRef.current = false;
        if (isMounted) {
          setIsLoadingHistory(false);
        }
      }
    };

    loadChatHistory();
    
    // Cleanup function
    return () => {
      isMounted = false;
      // Ensure loading state is cleared on unmount
      isLoadingHistoryRef.current = false;
    };
  }, [workspaceId, toast]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Focus input when component is shown (workspaceId becomes available)
  useEffect(() => {
    if (workspaceId && inputRef.current) {
      // Small delay to ensure component is fully rendered
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    }
  }, [workspaceId]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading || !workspaceId) return;

    const messageContent = inputValue.trim();
    setInputValue('');
    
    // Reset textarea height
    if (inputRef.current) {
      inputRef.current.style.height = '40px';
    }
    
    // Create and add user message immediately
    const userMessage: UIMessage = {
      id: `temp-${Date.now()}`,
      content: messageContent,
      role: 'user',
      workspace_id: workspaceId,
      timestamp: new Date(),
      is_sql_query: false
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Call the AI API endpoint which automatically stores chat messages
      const aiResponse = await workspaceApi.queryWithAI(workspaceId, messageContent);
      
      // Reload chat history to get the AI response
      const chatMessages = await workspaceApi.getChatMessages(workspaceId);
      const uiMessages = chatMessages.map(convertToUIMessage);
      setMessages(uiMessages);
      
      // If the AI response contains a SQL query, pass it to the QueryRunner
      if (aiResponse.sql_query && onSqlQuery) {
        onSqlQuery(aiResponse.sql_query);
      }
      
      // If onQuery callback is provided, call it with the user's query
      if (onQuery) {
        await onQuery(messageContent);
      }
    } catch (error) {
      console.error('Failed to get AI response:', error);
      toast({
        title: 'Error',
        description: 'Failed to get AI response. Please try again.',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
      
      // On error, reload chat history to get the current state
      try {
        const chatMessages = await workspaceApi.getChatMessages(workspaceId);
        const uiMessages = chatMessages.map(convertToUIMessage);
        setMessages(uiMessages);
      } catch (historyError) {
        console.error('Failed to reload chat history after error:', historyError);
      }
    } finally {
      setIsLoading(false);
      // Focus back on input
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Send message with Ctrl+Enter or Cmd+Enter
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSendMessage();
    }
    // Allow regular Enter for line breaks in textarea
    // Shift+Enter also creates line breaks (default behavior)
  };

  // Auto-resize textarea based on content
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);
    
    // Auto-resize textarea
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const handleClearChat = async () => {
    if (!workspaceId) return;
    
    try {
      await workspaceApi.clearChatMessages(workspaceId);
      setMessages([]);
      toast({
        title: 'Success',
        description: 'Chat history cleared',
        status: 'success',
        duration: 2000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Failed to clear chat:', error);
      toast({
        title: 'Error',
        description: 'Failed to clear chat history',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  // Don't render if no workspace ID
  if (!workspaceId) {
    return (
      <VStack spacing={4} flex={1} justify="center" align="center" p={8}>
        <Icon as={FiZap} boxSize={12} color="gray.300" />
        <Text color="gray.500" fontSize="lg" fontWeight="medium">
          AI Chat
        </Text>
        <Text color="gray.400" fontSize="sm" textAlign="center">
          Loading workspace... Please wait while we prepare your AI chat.
        </Text>
      </VStack>
    );
  }

  return (
    <VStack spacing={0} flex={1} minH={0}>
      {/* Messages Container */}
      <Box
        flex={1}
        width="100%"
        overflowY="auto"
        p={0}
        bg="gray.50"
        minH={0}
      >
        <VStack spacing={3} align="stretch" p={3}>
          {/* Loading state - only show when actually loading and no messages */}
          {isLoadingHistory && messages.length === 0 && (
            <Box textAlign="center" py={8}>
              <Spinner color="blue.500" mb={3} />
              <Text color="gray.500" fontSize="sm">
                Loading chat history...
              </Text>
            </Box>
          )}

          {/* Empty state - show only when not loading, no messages, and not currently sending a message */}
          {!isLoadingHistory && messages.length === 0 && !isLoading && (
            <Box textAlign="center" py={8}>
              <Icon as={FiZap} boxSize={8} color="gray.400" mb={3} />
              <Text color="gray.500" fontSize="sm" mb={2}>
                Start a conversation with AI
              </Text>
              <Text color="gray.400" fontSize="xs">
                Ask questions about your data, request insights, or get help with queries
              </Text>
            </Box>
          )}

          {messages.map((message: UIMessage) => {
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
                      if (onSqlQuery && sqlQuery) {
                        onSqlQuery(sqlQuery);
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
              <Box key={message.id} mb={3}>
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
          })}

          {isLoading && (
            <Flex justify="flex-start" px={1}>
              <Box
                bg="white"
                px={3}
                py={2}
                borderRadius="md"
                boxShadow="sm"
                border="1px"
                borderColor="gray.200"
              >
                <Flex align="center" gap={2} mb={1}>
                  <Icon as={FiZap} boxSize={3} color="blue.500" />
                  <Text fontSize="xs" color="gray.600">
                    AI
                  </Text>
                </Flex>
                <Text fontSize="sm" color="gray.600">
                  <Spinner size="xs" /> Thinking...
                </Text>
              </Box>
            </Flex>
          )}
        </VStack>
        <div ref={messagesEndRef} />
      </Box>

      {/* Input Area */}
      <Box
        width="100%"
        p={3}
        pb={1}
        borderTop="1px"
        borderColor="gray.200"
        bg="white"
        flexShrink={0}
      >
        <VStack spacing={0} align="stretch">
          <Textarea
            ref={inputRef}
            placeholder={workspaceId ? "Ask about your data" : "Select a workspace to chat"}
            value={inputValue}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            size="sm"
            disabled={isLoading || !workspaceId}
            flex={1}
            minH="70px"
            maxH="120px"
            py={2}
            pb={0}
            px={2}
            resize="none"
            rows={inputValue.split('\n').length}
          />
            <Flex width="100%" justify="space-between" align="flex-end">
            <Tooltip 
              label="Clear chat" 
              placement="top"
              hasArrow
            >
              <IconButton
              aria-label="Clear chat"
              icon={<Icon as={FiTrash2} />}
              onClick={handleClearChat}
              isDisabled={messages.length === 0 || isLoading || !workspaceId}
              colorScheme="gray"
              variant="ghost"
              size="sm"
              mt={1}
              />
            </Tooltip>
            <Tooltip 
              label="Send message (Ctrl+Enter)" 
              placement="top"
              hasArrow
            >
              <IconButton
              aria-label="Send message (Ctrl+Enter)"
              icon={<Icon as={FiSend} />}
              onClick={handleSendMessage}
              isDisabled={!inputValue.trim() || isLoading || !workspaceId}
              isLoading={isLoading}
              colorScheme="blue"
              variant="ghost"
              size="sm"
              mt={1}
              />
            </Tooltip>
            </Flex>
        </VStack>
      </Box>
    </VStack>
  );
};

export default ChatInterface;