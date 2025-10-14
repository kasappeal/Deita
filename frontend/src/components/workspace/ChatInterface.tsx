import {
  Box,
  Button,
  Flex,
  Icon,
  Spinner,
  Text,
  VStack,
  useToast
} from '@chakra-ui/react';
import React, { useEffect, useRef, useState } from 'react';
import { FiLock, FiZap } from 'react-icons/fi';
import { useAuth } from '../../contexts/AuthContext';
import { ChatMessage, workspaceApi } from '../../services/api';
import SignInModal from '../auth/SignInModal';
import ChatInput from './ChatInput';
import MessageBubble, { UIMessage } from './MessageBubble';

interface ChatInterfaceProps {
  workspaceId?: string;
  onQuery?: (query: string) => Promise<unknown>;
  onSqlQuery?: (sqlQuery: string) => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ workspaceId, onQuery, onSqlQuery }) => {
  const [messages, setMessages] = useState<UIMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [isSignInModalOpen, setIsSignInModalOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const isLoadingHistoryRef = useRef(false);
  const toast = useToast();
  const { isAuthenticated } = useAuth();

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
      // Only load if authenticated and workspace is available
      if (!workspaceId || !isAuthenticated) return;
      
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
  }, [workspaceId, isAuthenticated, toast]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Focus input when component is shown (workspaceId becomes available and user is authenticated)
  useEffect(() => {
    if (workspaceId && isAuthenticated) {
      // Small delay to ensure component is fully rendered
      setTimeout(() => {
        // Focus is handled by the ChatInput component
      }, 100);
    }
  }, [workspaceId, isAuthenticated]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading || !workspaceId || !isAuthenticated) return;

    const messageContent = inputValue.trim();
    setInputValue('');
    
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
    }
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

  // Show authentication required state if not authenticated
  if (!isAuthenticated) {
    return (
      <>
        <VStack spacing={4} flex={1} justify="center" align="center" p={8}>
          <Icon as={FiLock} boxSize={12} color="gray.300" />
          <Text color="gray.500" fontSize="lg" fontWeight="medium">
            Sign in to use AI Chat
          </Text>
          <Button
            colorScheme="blue"
            size="md"
            onClick={() => setIsSignInModalOpen(true)}
          >
            Sign In
          </Button>
        </VStack>
        <SignInModal
          isOpen={isSignInModalOpen}
          onClose={() => setIsSignInModalOpen(false)}
        />
      </>
    );
  }

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

          {messages.map((message: UIMessage) => (
            <MessageBubble
              key={message.id}
              message={message}
              onSqlClick={onSqlQuery}
            />
          ))}

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
      <ChatInput
        value={inputValue}
        isLoading={isLoading}
        isAuthenticated={isAuthenticated}
        workspaceId={workspaceId}
        onValueChange={setInputValue}
        onSend={handleSendMessage}
        onClear={handleClearChat}
      />
    </VStack>
  );
};

export default ChatInterface;