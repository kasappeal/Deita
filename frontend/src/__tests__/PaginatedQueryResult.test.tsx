import { ChakraProvider } from '@chakra-ui/react';
import '@testing-library/jest-dom';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import React from 'react';
import PaginatedQueryResult from '../components/query/PaginatedQueryResult';
import { workspaceApi } from '../services/api';

// Mock the API service
jest.mock('../services/api', () => ({
  workspaceApi: {
    executeQuery: jest.fn(),
    exportQueryAsCsv: jest.fn(),
    saveQuery: jest.fn(),
  },
}));

const mockExecuteQuery = workspaceApi.executeQuery as jest.MockedFunction<typeof workspaceApi.executeQuery>;
const mockExportQueryAsCsv = workspaceApi.exportQueryAsCsv as jest.MockedFunction<typeof workspaceApi.exportQueryAsCsv>;

const mockResult = {
  columns: ['id', 'name', 'value'],
  rows: [
    [1, 'Test 1', 100],
    [2, 'Test 2', 200],
    [3, 'Test 3', 300],
  ],
  has_more: true,
  time: 0.1,
};

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ChakraProvider>
    {children}
  </ChakraProvider>
);

describe('PaginatedQueryResult', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Set up default mock behavior for executeQuery
    mockExecuteQuery.mockImplementation((_workspaceId, _query, _page, _signal, count = false) => {
      if (count) {
        // Count query - return count result
        return Promise.resolve({
          columns: ['count'],
          rows: [[1500]],
          has_more: false,
          time: 0.001,
        });
      } else {
        // Regular query - return mock data
        return Promise.resolve(mockResult);
      }
    });
  });

  it('renders initial results with pagination message', () => {
    render(
      <TestWrapper>
        <PaginatedQueryResult
          workspaceId="test-workspace"
          query="SELECT * FROM test"
          initialResult={mockResult}
        />
      </TestWrapper>
    );

    // Check that the pagination message is displayed
    expect(screen.getByText('Showing first 3 rows of')).toBeInTheDocument();
    
    // Check that table data is displayed
    expect(screen.getByText('Test 1')).toBeInTheDocument();
    expect(screen.getByText('Test 2')).toBeInTheDocument();
    expect(screen.getByText('Test 3')).toBeInTheDocument();
  });

  it('updates results when initialResult prop changes', () => {
    const initialResult = {
      columns: ['id', 'name'],
      rows: [[1, 'Original Data']],
      has_more: false,
      time: 0.1,
    };

    const newResult = {
      columns: ['id', 'name'],
      rows: [[2, 'Updated Data']],
      has_more: false,
      time: 0.2,
    };

    const { rerender } = render(
      <TestWrapper>
        <PaginatedQueryResult
          workspaceId="test-workspace"
          query="SELECT * FROM test"
          initialResult={initialResult}
        />
      </TestWrapper>
    );

    // Check initial data is displayed
    expect(screen.getByText('Original Data')).toBeInTheDocument();

    // Update the prop with new data
    rerender(
      <TestWrapper>
        <PaginatedQueryResult
          workspaceId="test-workspace"
          query="SELECT * FROM test2"
          initialResult={newResult}
        />
      </TestWrapper>
    );

    // Check that new data is displayed
    expect(screen.getByText('Updated Data')).toBeInTheDocument();
    expect(screen.queryByText('Original Data')).not.toBeInTheDocument();
  });

  it('fetches and displays total count when count button is clicked', async () => {
    const countResult = {
      columns: ['count'],
      rows: [[1500]],
      has_more: false,
      time: 0.05,
    };

    mockExecuteQuery.mockResolvedValueOnce(countResult);

    render(
      <TestWrapper>
        <PaginatedQueryResult
          workspaceId="test-workspace"
          query="SELECT * FROM test"
          initialResult={mockResult}
        />
      </TestWrapper>
    );

    // Initially shows ? for count
    expect(screen.getByText('?')).toBeInTheDocument();
    expect(screen.getByText('Showing first 3 rows of')).toBeInTheDocument();

    // Click the count button
    fireEvent.click(screen.getByText('?'));

    // Wait for the count query to complete
    await waitFor(() => {
      expect(mockExecuteQuery).toHaveBeenCalledWith('test-workspace', 'SELECT * FROM test', 1, undefined, true);
    });

    // Check that count is displayed in button and pagination message is updated
    await waitFor(() => {
      expect(screen.getByText('1,500')).toBeInTheDocument();
      expect(screen.getByText('Showing 1 to 3 of 1,500')).toBeInTheDocument();
    });
  });

  it('renders navigation buttons correctly', () => {
    render(
      <TestWrapper>
        <PaginatedQueryResult
          workspaceId="test-workspace"
          query="SELECT * FROM test"
          initialResult={mockResult}
        />
      </TestWrapper>
    );

    expect(screen.getByText('Showing first 3 rows of')).toBeInTheDocument();

    // Check that navigation buttons are rendered and use aria-labels, not text
    expect(screen.getByRole('button', { name: /previous results/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /next results/i })).toBeInTheDocument();

    // Check that Previous button is disabled (page 1)
    expect(screen.getByRole('button', { name: /previous results/i })).toBeDisabled();

    // Check that Next button is enabled (has_more = true)
    expect(screen.getByRole('button', { name: /next results/i })).not.toBeDisabled();
  });

  it('handles next page navigation', async () => {
    const nextPageResult = {
      columns: ['id', 'name', 'value'],
      rows: [
        [4, 'Test 4', 400],
        [5, 'Test 5', 500],
      ],
      has_more: false,
      time: 0.05,
    };

    // Override the default mock for this test
    mockExecuteQuery.mockImplementation((_workspaceId, _query, page, _signal, count = false) => {
      if (count) {
        return Promise.resolve({
          columns: ['count'],
          rows: [[1500]],
          has_more: false,
          time: 0.001,
        });
      } else if (page === 2) {
        return Promise.resolve(nextPageResult);
      } else {
        return Promise.resolve(mockResult);
      }
    });

    render(
      <TestWrapper>
        <PaginatedQueryResult
          workspaceId="test-workspace"
          query="SELECT * FROM test"
          initialResult={mockResult}
        />
      </TestWrapper>
    );

    // Click Next button
    fireEvent.click(screen.getByRole('button', { name: /next results/i }));

    // Wait for API call and state update
    await waitFor(() => {
      expect(mockExecuteQuery).toHaveBeenCalledWith('test-workspace', 'SELECT * FROM test', 2);
    });

    // Check that pagination message updated for last page
    await waitFor(() => {
      expect(screen.getByText('Showing last 2 rows')).toBeInTheDocument();
    });
  });

  it('shows correct pagination message for middle pages', async () => {
    const middlePageResult = {
      columns: ['id', 'name', 'value'],
      rows: [
        [4, 'Test 4', 400],
        [5, 'Test 5', 500],
        [6, 'Test 6', 600],
      ],
      has_more: true,
      time: 0.08,
    };

    // Override the default mock for this test
    mockExecuteQuery.mockImplementation((_workspaceId, _query, page, _signal, count = false) => {
      if (count) {
        return Promise.resolve({
          columns: ['count'],
          rows: [[1500]],
          has_more: false,
          time: 0.001,
        });
      } else if (page === 2) {
        return Promise.resolve(middlePageResult);
      } else {
        return Promise.resolve(mockResult);
      }
    });

    render(
      <TestWrapper>
        <PaginatedQueryResult
          workspaceId="test-workspace"
          query="SELECT * FROM test"
          initialResult={mockResult}
        />
      </TestWrapper>
    );

    // Click Next button to go to page 2
    fireEvent.click(screen.getByRole('button', { name: /next results/i }));

    await waitFor(() => {
      expect(screen.getByText('Showing rows 4 to 6')).toBeInTheDocument();
    });

    // Both buttons should be enabled on middle page
    expect(screen.getByRole('button', { name: /previous results/i })).not.toBeDisabled();
    expect(screen.getByRole('button', { name: /next results/i })).not.toBeDisabled();
  });

  it('handles API errors gracefully', async () => {
    // Override the default mock for this test to throw error on page 2
    mockExecuteQuery.mockImplementation((_workspaceId, _query, page, _signal, count = false) => {
      if (count) {
        return Promise.resolve({
          columns: ['count'],
          rows: [[1500]],
          has_more: false,
          time: 0.001,
        });
      } else if (page === 2) {
        return Promise.reject(new Error('API Error'));
      } else {
        return Promise.resolve(mockResult);
      }
    });

    render(
      <TestWrapper>
        <PaginatedQueryResult
          workspaceId="test-workspace"
          query="SELECT * FROM test"
          initialResult={mockResult}
        />
      </TestWrapper>
    );

    // Click Next button
    fireEvent.click(screen.getByRole('button', { name: /next results/i }));

    // Wait for error handling
    await waitFor(() => {
      expect(mockExecuteQuery).toHaveBeenCalled();
    });

    // Should still show original results
    expect(screen.getByText('Showing first 3 rows of')).toBeInTheDocument();
  });

  it('shows exporting toast when exporting data to CSV', async () => {
    // Mock the export function
    const mockBlob = new Blob(['test,data\n1,2\n'], { type: 'text/csv' });
    mockExportQueryAsCsv.mockResolvedValue(mockBlob);

    // Mock URL methods
    window.URL.createObjectURL = jest.fn(() => 'blob:mock-url');
    window.URL.revokeObjectURL = jest.fn();

    render(
      <TestWrapper>
        <PaginatedQueryResult
          workspaceId="test-workspace"
          query="SELECT * FROM test"
          initialResult={mockResult}
        />
      </TestWrapper>
    );

    // Click the export button
    const exportButton = screen.getByRole('button', { name: /export/i });
    fireEvent.click(exportButton);

    // Wait for the exporting toast to appear
    await waitFor(() => {
      expect(screen.getByText('Exporting your data')).toBeInTheDocument();
    });

    // Should show a message about time to export
    await waitFor(() => {
      expect(screen.getByText(/It can take some time to export/)).toBeInTheDocument();
    });

    // Wait for export to complete
    await waitFor(() => {
      expect(mockExportQueryAsCsv).toHaveBeenCalledWith('test-workspace', 'SELECT * FROM test');
    });

    // Wait for success toast
    await waitFor(() => {
      expect(screen.getByText('Export Successful')).toBeInTheDocument();
    });
  });

  it('shows exporting toast with row count when totalCount is already available', async () => {
    // Mock the export function
    const mockBlob = new Blob(['test,data\n1,2\n'], { type: 'text/csv' });
    mockExportQueryAsCsv.mockResolvedValue(mockBlob);

    // Mock URL methods
    window.URL.createObjectURL = jest.fn(() => 'blob:mock-url');
    window.URL.revokeObjectURL = jest.fn();

    const countResult = {
      columns: ['count'],
      rows: [[1500]],
      has_more: false,
      time: 0.05,
    };

    mockExecuteQuery.mockResolvedValueOnce(countResult);

    render(
      <TestWrapper>
        <PaginatedQueryResult
          workspaceId="test-workspace"
          query="SELECT * FROM test"
          initialResult={mockResult}
        />
      </TestWrapper>
    );

    // First, fetch the count
    fireEvent.click(screen.getByText('?'));

    await waitFor(() => {
      expect(screen.getByText('1,500')).toBeInTheDocument();
    });

    // Now click export
    const exportButton = screen.getByRole('button', { name: /export/i });
    fireEvent.click(exportButton);

    // Should show exporting toast with specific row count
    await waitFor(() => {
      expect(screen.getByText('Exporting your data')).toBeInTheDocument();
      expect(screen.getByText('It can take some time to export 1,500 rows')).toBeInTheDocument();
    });

    // Wait for export to complete
    await waitFor(() => {
      expect(mockExportQueryAsCsv).toHaveBeenCalledWith('test-workspace', 'SELECT * FROM test');
    });

    // Wait for success toast
    await waitFor(() => {
      expect(screen.getByText('Export Successful')).toBeInTheDocument();
    });
  });
});