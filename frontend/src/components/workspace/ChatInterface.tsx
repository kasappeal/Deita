import {
    Box,
    Flex,
    Icon,
    IconButton,
    Input,
    Text,
    VStack,
    useToast,
} from '@chakra-ui/react';
import React, { useEffect, useRef, useState } from 'react';
import { FiSend, FiUser, FiZap } from 'react-icons/fi';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
}

interface ChatInterfaceProps {
  workspaceId?: string;
  onQuery?: (query: string) => Promise<unknown>;
}

const ChatInterface: React.FC<ChatInterfaceProps> = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const toast = useToast();

  const scrollToBottom = () => {
    if (messagesEndRef.current && typeof messagesEndRef.current.scrollIntoView === 'function') {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue.trim(),
      role: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // For now, we'll simulate an AI response
      // In the future, this will call the actual AI API
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: `I understand you want to: "${userMessage.content}". AI functionality is being developed and will be available soon. For now, you can use the SQL tab to write queries directly.`,
        role: 'assistant',
        timestamp: new Date(),
      };

      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setMessages(prev => [...prev, aiResponse]);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to get AI response. Please try again.',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
      // Focus back on input
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <VStack spacing={0} flex={1} minH={0}>
      {/* Messages Container */}
      <Box
        flex={1}
        width="100%"
        overflowY="auto"
        p={3}
        bg="gray.50"
        minH={0}
      >
        <VStack spacing={3} align="stretch" p={2}>
          {messages.length === 0 && (
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

          {messages.map((message) => (
            <Flex
              key={message.id}
              justify={message.role === 'user' ? 'flex-end' : 'flex-start'}
              px={2}
            >
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
          ))}

          {isLoading && (
            <Flex justify="flex-start" px={2}>
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
                  Thinking...
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
        p={4}
        borderTop="1px"
        borderColor="gray.200"
        bg="white"
        flexShrink={0}
      >
        <Flex gap={3} align="flex-end">
          <Input
            ref={inputRef}
            placeholder="Ask about your data..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            size="md"
            disabled={isLoading}
            flex={1}
            minH="40px"
            py={2}
          />
          <IconButton
            aria-label="Send message"
            icon={<Icon as={FiSend} />}
            onClick={handleSendMessage}
            isDisabled={!inputValue.trim() || isLoading}
            isLoading={isLoading}
            colorScheme="blue"
            size="md"
            minW="40px"
            h="40px"
          />
        </Flex>
      </Box>
    </VStack>
  );
};

export default ChatInterface;