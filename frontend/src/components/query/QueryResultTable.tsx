import {
    Box,
    Table,
    TableContainer,
    Tbody,
    Td,
    Th,
    Thead,
    Tr
} from '@chakra-ui/react';
import React from 'react';

export interface QueryResultData {
  columns: string[];
  rows: (string | number | boolean | null)[][];
}

interface QueryResultTableProps {
  result: QueryResultData | null;
}

const QueryResultTable: React.FC<QueryResultTableProps> = ({ result }) => {
  if (!result || !Array.isArray(result.rows) || !result.columns) return null;
  return (
    <Box bg="white" overflowX="auto" width={"100%"}>
      <TableContainer>
        <Table size='sm'>
            <Thead>
            <Tr>
                {result.columns.map((col) => (
                <Th key={col}>{col}</Th>
                ))}
            </Tr>
            </Thead>
            <Tbody>
            {result.rows.map((row, i) => (
                <Tr key={i}>
                {row.map((cell, j) => (
                    <Td key={j}>{cell === null ? <span style={{ color: '#bbb' }}>NULL</span> : String(cell)}</Td>
                ))}
                </Tr>
            ))}
            </Tbody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default QueryResultTable;
