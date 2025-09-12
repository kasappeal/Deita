import React from 'react'
import { Box, Flex, Heading, HStack, Link, Button } from '@chakra-ui/react'

const Header: React.FC = () => {
  return (
    <Box bg="white" shadow="sm" borderBottom="1px" borderColor="gray.200">
      <Flex maxW="container.xl" mx="auto" px={4} py={4} justify="space-between" align="center">
        {/* Logo */}
        <Heading as="h1" size="lg" color="blue.600">
          Deita
        </Heading>

        {/* Navigation */}
        <HStack spacing={6}>
          <Link href="/" color="gray.600" _hover={{ color: 'blue.600' }}>
            Home
          </Link>
          <Link href="/explore" color="gray.600" _hover={{ color: 'blue.600' }}>
            Explore
          </Link>
          <Link href="/docs" color="gray.600" _hover={{ color: 'blue.600' }}>
            Docs
          </Link>
        </HStack>

        {/* Actions */}
        <HStack spacing={3}>
          <Button variant="ghost" size="sm">
            Sign In
          </Button>
          <Button colorScheme="blue" size="sm">
            Get Started
          </Button>
        </HStack>
      </Flex>
    </Box>
  )
}

export default Header
