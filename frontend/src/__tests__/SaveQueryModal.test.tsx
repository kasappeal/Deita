import { ChakraProvider } from '@chakra-ui/react';
import '@testing-library/jest-dom';
import { fireEvent, render, screen } from '@testing-library/react';
import React from 'react';
import SaveQueryModal from '../components/query/SaveQueryModal';

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ChakraProvider>
    {children}
  </ChakraProvider>
);

describe('SaveQueryModal', () => {
  const mockOnClose = jest.fn();
  const mockOnQueryNameChange = jest.fn();
  const mockOnSave = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders modal when isOpen is true', () => {
    render(
      <TestWrapper>
        <SaveQueryModal
          isOpen={true}
          queryName=""
          saving={false}
          onClose={mockOnClose}
          onQueryNameChange={mockOnQueryNameChange}
          onSave={mockOnSave}
        />
      </TestWrapper>
    );

    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Enter a name for this query')).toBeInTheDocument();
  });

  it('does not render modal when isOpen is false', () => {
    render(
      <TestWrapper>
        <SaveQueryModal
          isOpen={false}
          queryName=""
          saving={false}
          onClose={mockOnClose}
          onQueryNameChange={mockOnQueryNameChange}
          onSave={mockOnSave}
        />
      </TestWrapper>
    );

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('calls onQueryNameChange when input value changes', () => {
    render(
      <TestWrapper>
        <SaveQueryModal
          isOpen={true}
          queryName=""
          saving={false}
          onClose={mockOnClose}
          onQueryNameChange={mockOnQueryNameChange}
          onSave={mockOnSave}
        />
      </TestWrapper>
    );

    const input = screen.getByPlaceholderText('Enter a name for this query');
    fireEvent.change(input, { target: { value: 'My Query' } });
    expect(mockOnQueryNameChange).toHaveBeenCalledWith('My Query');
  });

  it('calls onClose when cancel button is clicked', () => {
    render(
      <TestWrapper>
        <SaveQueryModal
          isOpen={true}
          queryName="Test Query"
          saving={false}
          onClose={mockOnClose}
          onQueryNameChange={mockOnQueryNameChange}
          onSave={mockOnSave}
        />
      </TestWrapper>
    );

    fireEvent.click(screen.getByText('Cancel'));
    expect(mockOnClose).toHaveBeenCalled();
  });

  it('calls onSave when save button is clicked', () => {
    render(
      <TestWrapper>
        <SaveQueryModal
          isOpen={true}
          queryName="Test Query"
          saving={false}
          onClose={mockOnClose}
          onQueryNameChange={mockOnQueryNameChange}
          onSave={mockOnSave}
        />
      </TestWrapper>
    );

    const buttons = screen.getAllByRole('button');
    const saveButton = buttons.find(btn => btn.textContent === 'Save Query');
    fireEvent.click(saveButton!);
    expect(mockOnSave).toHaveBeenCalled();
  });

  it('disables save button when query name is empty', () => {
    render(
      <TestWrapper>
        <SaveQueryModal
          isOpen={true}
          queryName=""
          saving={false}
          onClose={mockOnClose}
          onQueryNameChange={mockOnQueryNameChange}
          onSave={mockOnSave}
        />
      </TestWrapper>
    );

    const buttons = screen.getAllByRole('button');
    const saveButton = buttons.find(btn => btn.textContent === 'Save Query');
    expect(saveButton).toBeDisabled();
  });

  it('shows loading state when saving is true', () => {
    render(
      <TestWrapper>
        <SaveQueryModal
          isOpen={true}
          queryName="Test Query"
          saving={true}
          onClose={mockOnClose}
          onQueryNameChange={mockOnQueryNameChange}
          onSave={mockOnSave}
        />
      </TestWrapper>
    );

    const buttons = screen.getAllByRole('button');
    const saveButton = buttons.find(btn => btn.textContent?.includes('Save Query') || btn.getAttribute('aria-label')?.includes('Save'));
    expect(saveButton).toBeDefined();
    expect(saveButton).toBeDisabled();
  });

  it('calls onSave when Enter key is pressed with valid query name', () => {
    render(
      <TestWrapper>
        <SaveQueryModal
          isOpen={true}
          queryName="Test Query"
          saving={false}
          onClose={mockOnClose}
          onQueryNameChange={mockOnQueryNameChange}
          onSave={mockOnSave}
        />
      </TestWrapper>
    );

    const input = screen.getByPlaceholderText('Enter a name for this query');
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });
    expect(mockOnSave).toHaveBeenCalled();
  });

  it('does not call onSave when Enter key is pressed with empty query name', () => {
    render(
      <TestWrapper>
        <SaveQueryModal
          isOpen={true}
          queryName=""
          saving={false}
          onClose={mockOnClose}
          onQueryNameChange={mockOnQueryNameChange}
          onSave={mockOnSave}
        />
      </TestWrapper>
    );

    const input = screen.getByPlaceholderText('Enter a name for this query');
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });
    expect(mockOnSave).not.toHaveBeenCalled();
  });
});
