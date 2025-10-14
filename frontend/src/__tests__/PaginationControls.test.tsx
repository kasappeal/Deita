import { ChakraProvider } from '@chakra-ui/react';
import '@testing-library/jest-dom';
import { fireEvent, render, screen } from '@testing-library/react';
import React from 'react';
import PaginationControls from '../components/query/PaginationControls';

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ChakraProvider>
    {children}
  </ChakraProvider>
);

describe('PaginationControls', () => {
  const mockOnFirstPage = jest.fn();
  const mockOnPreviousPage = jest.fn();
  const mockOnNextPage = jest.fn();
  const mockOnLastPage = jest.fn();
  const mockOnSaveQuery = jest.fn();
  const mockOnExport = jest.fn();
  const mockOnFetchCount = jest.fn();

  const defaultProps = {
    currentPage: 1,
    hasMore: true,
    totalCount: null,
    loading: false,
    countLoading: false,
    exporting: false,
    saving: false,
    paginationMessage: 'Showing first 10 rows of',
    onFirstPage: mockOnFirstPage,
    onPreviousPage: mockOnPreviousPage,
    onNextPage: mockOnNextPage,
    onLastPage: mockOnLastPage,
    onSaveQuery: mockOnSaveQuery,
    onExport: mockOnExport,
    onFetchCount: mockOnFetchCount,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders all navigation buttons', () => {
    render(
      <TestWrapper>
        <PaginationControls {...defaultProps} />
      </TestWrapper>
    );

    expect(screen.getByRole('button', { name: /go to first results/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /previous results/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /next results/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /last results/i })).toBeInTheDocument();
  });

  it('renders save and export buttons', () => {
    render(
      <TestWrapper>
        <PaginationControls {...defaultProps} />
      </TestWrapper>
    );

    expect(screen.getByRole('button', { name: /save query/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /export/i })).toBeInTheDocument();
  });

  it('displays pagination message', () => {
    render(
      <TestWrapper>
        <PaginationControls {...defaultProps} />
      </TestWrapper>
    );

    expect(screen.getByText('Showing first 10 rows of')).toBeInTheDocument();
  });

  it('displays total count when available', () => {
    render(
      <TestWrapper>
        <PaginationControls {...defaultProps} totalCount={1500} />
      </TestWrapper>
    );

    expect(screen.getByText('1,500')).toBeInTheDocument();
  });

  it('displays question mark when total count is not available', () => {
    render(
      <TestWrapper>
        <PaginationControls {...defaultProps} totalCount={null} />
      </TestWrapper>
    );

    expect(screen.getByText('?')).toBeInTheDocument();
  });

  it('disables previous and first buttons on first page', () => {
    render(
      <TestWrapper>
        <PaginationControls {...defaultProps} currentPage={1} />
      </TestWrapper>
    );

    expect(screen.getByRole('button', { name: /go to first results/i })).toBeDisabled();
    expect(screen.getByRole('button', { name: /previous results/i })).toBeDisabled();
  });

  it('enables previous and first buttons when not on first page', () => {
    render(
      <TestWrapper>
        <PaginationControls {...defaultProps} currentPage={2} />
      </TestWrapper>
    );

    expect(screen.getByRole('button', { name: /go to first results/i })).not.toBeDisabled();
    expect(screen.getByRole('button', { name: /previous results/i })).not.toBeDisabled();
  });

  it('disables next and last buttons when hasMore is false', () => {
    render(
      <TestWrapper>
        <PaginationControls {...defaultProps} hasMore={false} />
      </TestWrapper>
    );

    expect(screen.getByRole('button', { name: /next results/i })).toBeDisabled();
    expect(screen.getByRole('button', { name: /last results/i })).toBeDisabled();
  });

  it('calls handler functions when buttons are clicked', () => {
    render(
      <TestWrapper>
        <PaginationControls {...defaultProps} currentPage={2} />
      </TestWrapper>
    );

    fireEvent.click(screen.getByRole('button', { name: /go to first results/i }));
    expect(mockOnFirstPage).toHaveBeenCalled();

    fireEvent.click(screen.getByRole('button', { name: /previous results/i }));
    expect(mockOnPreviousPage).toHaveBeenCalled();

    fireEvent.click(screen.getByRole('button', { name: /next results/i }));
    expect(mockOnNextPage).toHaveBeenCalled();

    fireEvent.click(screen.getByRole('button', { name: /last results/i }));
    expect(mockOnLastPage).toHaveBeenCalled();

    fireEvent.click(screen.getByRole('button', { name: /save query/i }));
    expect(mockOnSaveQuery).toHaveBeenCalled();

    fireEvent.click(screen.getByRole('button', { name: /export/i }));
    expect(mockOnExport).toHaveBeenCalled();
  });

  it('calls onFetchCount when count button is clicked', () => {
    render(
      <TestWrapper>
        <PaginationControls {...defaultProps} />
      </TestWrapper>
    );

    fireEvent.click(screen.getByText('?'));
    expect(mockOnFetchCount).toHaveBeenCalled();
  });

  it('disables all buttons when loading is true', () => {
    render(
      <TestWrapper>
        <PaginationControls {...defaultProps} loading={true} currentPage={2} />
      </TestWrapper>
    );

    expect(screen.getByRole('button', { name: /go to first results/i })).toBeDisabled();
    expect(screen.getByRole('button', { name: /previous results/i })).toBeDisabled();
    expect(screen.getByRole('button', { name: /next results/i })).toBeDisabled();
    expect(screen.getByRole('button', { name: /last results/i })).toBeDisabled();
    expect(screen.getByRole('button', { name: /save query/i })).toBeDisabled();
    expect(screen.getByRole('button', { name: /export/i })).toBeDisabled();
  });
});
