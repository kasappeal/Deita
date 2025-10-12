import { Box, Button, CircularProgress, Flex, FormControl, FormLabel, Heading, HStack, Icon, IconButton, Input, Modal, ModalBody, ModalContent, ModalFooter, ModalHeader, ModalOverlay, Select, Tooltip, useDisclosure, useToast } from '@chakra-ui/react';
import React, { useEffect, useMemo, useState } from 'react';
import { Link as RouterLink, useLocation, useNavigate } from 'react-router-dom';

import { FiAlertTriangle, FiGlobe, FiGrid, FiLock, FiPlus, FiSettings } from 'react-icons/fi';

import { useAuth, Workspace } from '../../contexts/AuthContext';
import { workspaceApi } from '../../services/api';
import SignInModal from '../auth/SignInModal';

// Workspace settings modal component
const WorkspaceSettingsModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  workspace: Workspace;
  onWorkspaceUpdated: (updated: Workspace) => void;
}> = ({ isOpen, onClose, workspace, onWorkspaceUpdated }) => {
  const [name, setName] = useState(workspace?.name || '');
  const [visibility, setVisibility] = useState(workspace?.visibility || 'public');
  const [saving, setSaving] = useState(false);
  const toast = useToast();

  useEffect(() => {
    setName(workspace?.name || '');
    setVisibility(workspace?.visibility || 'public');
  }, [workspace, isOpen]);

  const handleSave = async () => {
    if (!workspace?.id) return;
    setSaving(true);
    try {
      const updated = await workspaceApi.updateWorkspace(workspace.id, { name, visibility: visibility as 'public' | 'private' });
      toast({
        title: 'Workspace updated!',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      onWorkspaceUpdated(updated);
      onClose();
    } catch {
      toast({
        title: 'Error updating workspace',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setSaving(false);
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} isCentered>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Edit Workspace</ModalHeader>
        <ModalBody>
          <FormControl mb={4}>
            <FormLabel>Name</FormLabel>
            <Input value={name} onChange={e => setName(e.target.value)} />
          </FormControl>
          <FormControl>
            <FormLabel>Visibility</FormLabel>
            <Select value={visibility} onChange={e => setVisibility(e.target.value as 'public' | 'private')}>
              <option value="public">Public</option>
              <option value="private">Private</option>
            </Select>
          </FormControl>
        </ModalBody>
        <ModalFooter>
          <Button colorScheme="blue" mr={3} onClick={handleSave} isLoading={saving}>Save</Button>
          <Button variant="ghost" onClick={onClose}>Cancel</Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

const Header: React.FC = () => {
  const { workspace, isAuthenticated, logout, setWorkspace } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [isSignInModalOpen, setIsSignInModalOpen] = useState(false);
  const [isClaimModalOpen, setIsClaimModalOpen] = useState(false);
  const [claiming, setClaiming] = useState(false);
  const [isCreateWorkspaceModalOpen, setIsCreateWorkspaceModalOpen] = useState(false);
  const [workspaceName, setWorkspaceName] = useState('');
  const [creating, setCreating] = useState(false);
  const toast = useToast();

  const { isOpen: isSettingsOpen, onOpen: openSettings, onClose: closeSettings } = useDisclosure();

  const handleSignInClick = () => {
    setIsSignInModalOpen(true);
  };

  const handleLogoutClick = () => {
    logout();
  };


  // Workspace state for modal updates
  const [workspaceState, setWorkspaceState] = useState(workspace);
  useEffect(() => {
    setWorkspaceState(workspace);
  }, [workspace]);

  // Claim workspace handler
  const handleClaimWorkspace = async () => {
    if (!workspace?.id) return;
    setClaiming(true);
    try {
      // Call claimWorkspace API and reload workspace info
      const updated = await workspaceApi.claimWorkspace(workspace.id);
      toast({
        title: 'Workspace claimed!',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      setWorkspace(updated); // update context so header re-renders
      setWorkspaceState(updated);
      setIsClaimModalOpen(false);
    } catch {
      toast({
        title: 'Error claiming workspace',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setClaiming(false);
    }
  };

  // Generate random workspace name
  const generateRandomWorkspaceName = () => {
    const animals = ['Otter', 'Fox', 'Bear', 'Hawk', 'Wolf', 'Lynx', 'Seal', 'Crane', 'Swan', 'Panda'];
    const colors = ['Blue', 'Green', 'Red', 'Yellow', 'Purple', 'Orange', 'Silver', 'Gold', 'Indigo', 'Teal'];
    return `${colors[Math.floor(Math.random()*colors.length)]} ${animals[Math.floor(Math.random()*animals.length)]}`;
  };

  // Create workspace handler
  const handleCreateWorkspace = async () => {
    if (!workspaceName.trim()) return;
    setCreating(true);
    try {
      const newWorkspace = await workspaceApi.createWorkspace(workspaceName.trim());
      localStorage.setItem('lastVisitedWorkspaceId', newWorkspace.id);
      setIsCreateWorkspaceModalOpen(false);
      setWorkspaceName('');
      navigate(`/workspaces/${newWorkspace.id}`);
    } catch (error) {
      toast({
        title: 'Error creating workspace',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setCreating(false);
    }
  };

  // Open create workspace modal
  const handleCreateWorkspaceClick = () => {
    setWorkspaceName(generateRandomWorkspaceName());
    setIsCreateWorkspaceModalOpen(true);
  };

  // Distinguish between workspaces list page and individual workspace page
  const isWorkspacesListPage = useMemo(() => location.pathname === '/workspaces' || location.pathname === '/workspaces/', [location.pathname]);
  const isIndividualWorkspacePage = useMemo(() => /^\/workspaces\/[^/]+$/.test(location.pathname), [location.pathname]);

  // Clear workspace context when navigating to workspaces list page
  useEffect(() => {
    if (isWorkspacesListPage && workspace) {
      setWorkspace(null);
    }
  }, [isWorkspacesListPage, workspace, setWorkspace]);

  return (
    <>
      <Box bg="white" shadow="sm" borderBottom="1px" borderColor="gray.200">
        <Flex maxW="full" mx="auto" p={4} justify="space-between" align="center">
          {/* Logo */}
          <HStack spacing={2} align="center">
            <Heading as="h1" size="md" color="blue.600" display="flex" alignItems="center" style={{ cursor: 'pointer' }}>
              {isWorkspacesListPage ? (
                'Your workspaces'
              ) : isIndividualWorkspacePage && workspace ? (
                <>
                  {workspace.name}
                  {/* Show visibility icon */}
                  <Tooltip 
                    label={workspace.visibility === 'private' ? 'Private workspace' : 'Public workspace'} 
                    hasArrow
                  >
                    <Box>
                      <Icon
                        as={workspace.visibility === 'private' ? FiLock : FiGlobe}
                        color={workspace.visibility === 'private' ? 'red.500' : 'green.500'}
                        size="xs"
                        ml={2}
                      />
                    </Box>
                  </Tooltip>
                </>
              ) : 'Your workspaces - Deita'}
            </Heading>
          </HStack>

          {/* Right side controls */}
          <HStack>

            {/* Show warning icon if workspace has no owner */}
            {isIndividualWorkspacePage && workspace && workspace.is_orphan && (
              <Tooltip label="This workspace has no owner. Claim it." hasArrow>
                <IconButton
                  aria-label="Claim Workspace"
                  icon={<FiAlertTriangle color="#DD6B20" size={25} />} // Chakra orange.400
                  size="sm"
                  variant="ghost"
                  onClick={e => {
                    e.stopPropagation();
                    setIsClaimModalOpen(true);
                  }}
                />
              </Tooltip>
            )}

            {/* Show gear icon only if user is owner */}
            {isIndividualWorkspacePage && workspace && workspace.is_yours && (
              <Tooltip label="Workspace Settings" hasArrow>
                <IconButton
                  aria-label="Workspace Settings"
                  icon={<FiSettings size={20} />}
                  size="sm"
                  variant="ghost"
                  ml={2}
                  colorScheme="blue"
                  onClick={e => {
                    e.stopPropagation();
                    openSettings();
                  }}
                />
              </Tooltip>
            )}
            
            {/* Storage usage only on individual workspace page */}
            {isIndividualWorkspacePage && workspace && (
              (() => {
                const used = workspace.storage_used ?? 0;
                const max = workspace.max_storage ?? 1;
                const percent = Math.min(100, Math.round((used / max) * 100));
                const tooltipLabel = `Storage: ${percent}% - ${(used / (1024 * 1024)).toFixed(0)} of ${(max / (1024 * 1024)).toFixed(0)} MB`;
                return (
                  <Tooltip label={tooltipLabel} hasArrow>
                      <CircularProgress value={percent} size="20px" thickness='20px' color={percent > 90 ? 'red.400' : 'blue.400'} />
                  </Tooltip>
                );
              })()
            )}
            
            {/* Create workspace button only on workspaces list page */}
            {isWorkspacesListPage && isAuthenticated && (
              <Tooltip label="Create New Workspace" hasArrow>
                <IconButton
                  aria-label="Create Workspace"
                  icon={<FiPlus size={25} />}
                  size="sm"
                  variant="ghost"
                  colorScheme="blue"
                  onClick={handleCreateWorkspaceClick}
                />
              </Tooltip>
            )}

            {/* Workspace list button only on individual workspace page */}
            {isIndividualWorkspacePage && isAuthenticated && (
              <Tooltip label="Workspace List" hasArrow>
                <IconButton
                  as={RouterLink}
                  to="/workspaces"
                  aria-label="Workspaces"
                  icon={<FiGrid size={20} />}
                  size="sm"
                  variant="ghost"
                  colorScheme="blue"
                />
              </Tooltip>
            )}
            
            {isAuthenticated ? (
              <HStack>
                <Button colorScheme="gray" size="sm" onClick={handleLogoutClick}>
                  Logout
                </Button>
              </HStack>
            ) : (
              <Button colorScheme="blue" size="sm" onClick={handleSignInClick}>
                Sign In
              </Button>
            )}
          </HStack>
        </Flex>
      </Box>

      <SignInModal
        isOpen={isSignInModalOpen}
        onClose={() => setIsSignInModalOpen(false)}
      />

      {/* Claim workspace confirmation modal */}
      <Modal isOpen={isClaimModalOpen} onClose={() => setIsClaimModalOpen(false)} isCentered>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Claim Workspace</ModalHeader>
          <ModalBody>
            {isAuthenticated ? (
              <>Are you sure you want to claim ownership of this workspace? This action cannot be undone.</>
            ) : (
              <>
                You must be signed in to claim a workspace.<br />
                <Button colorScheme="blue" mt={4} onClick={() => { setIsClaimModalOpen(false); setIsSignInModalOpen(true); }}>
                  Sign In
                </Button>
              </>
            )}
          </ModalBody>
          {isAuthenticated && (
            <ModalFooter>
              <Button colorScheme="orange" mr={3} onClick={handleClaimWorkspace} isLoading={claiming}>
                Yes, Claim
              </Button>
              <Button variant="ghost" onClick={() => setIsClaimModalOpen(false)}>
                Cancel
              </Button>
            </ModalFooter>
          )}
        </ModalContent>
      </Modal>

      {/* Create workspace modal */}
      <Modal isOpen={isCreateWorkspaceModalOpen} onClose={() => setIsCreateWorkspaceModalOpen(false)} isCentered>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Create New Workspace</ModalHeader>
          <ModalBody>
            <FormControl>
              <FormLabel>Workspace Name</FormLabel>
              <Input
                value={workspaceName}
                onChange={(e) => setWorkspaceName(e.target.value)}
                placeholder="Enter workspace name"
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleCreateWorkspace();
                  }
                }}
              />
            </FormControl>
          </ModalBody>
          <ModalFooter>
            <Button
              colorScheme="blue"
              mr={3}
              onClick={handleCreateWorkspace}
              isLoading={creating}
              loadingText="Creating..."
              isDisabled={!workspaceName.trim()}
            >
              Create
            </Button>
            <Button variant="ghost" onClick={() => setIsCreateWorkspaceModalOpen(false)}>
              Cancel
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Workspace settings modal */}
      {isIndividualWorkspacePage && isAuthenticated && workspaceState && (
        <WorkspaceSettingsModal
          isOpen={isSettingsOpen}
          onClose={closeSettings}
          workspace={workspaceState}
          onWorkspaceUpdated={updated => {
            setWorkspaceState(updated);
            setWorkspace(updated); // Update main context so header title updates immediately
          }}
        />
      )}
    </>
  );
}

export default Header
