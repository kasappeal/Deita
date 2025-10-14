/**
 * SQL syntax validation utilities
 */

import Parser from 'node-sql-parser';

const parser = new Parser.Parser();

/**
 * SQL syntax validation using a proper SQL parser
 * Validates SQL syntax and checks for dangerous operations
 */
export function validateSqlSyntax(sql: string): { isValid: boolean; error?: string } {
  if (!sql || !sql.trim()) {
    return { isValid: false, error: 'Query cannot be empty' };
  }

  try {
    // Parse the SQL query
    const ast = parser.astify(sql, { database: 'PostgresQL' });
    
    // Ensure we have a valid AST
    if (!ast) {
      return { isValid: false, error: 'Invalid SQL syntax' };
    }

    // Convert to array if single statement
    const statements = Array.isArray(ast) ? ast : [ast];

    // Check if we have multiple statements (not allowed)
    if (statements.length > 1) {
      return { isValid: false, error: 'Multiple SQL statements are not allowed' };
    }

    // Check each statement
    for (const statement of statements) {
      // Only allow SELECT queries
      if (statement.type !== 'select') {
        return { 
          isValid: false, 
          error: `Only SELECT queries are allowed. Found: ${statement.type.toUpperCase()}` 
        };
      }

      // Check for dangerous operations in subqueries or CTEs
      if (containsDangerousOperations(statement)) {
        return { 
          isValid: false, 
          error: 'Query contains potentially dangerous SQL operations' 
        };
      }
    }

    return { isValid: true };
  } catch (error) {
    // Parser will throw an error for invalid SQL syntax
    const errorMessage = error instanceof Error ? error.message : 'Invalid SQL syntax';
    return { isValid: false, error: errorMessage };
  }
}

/**
 * Recursively check for dangerous SQL operations in AST
 */
function containsDangerousOperations(ast: unknown): boolean {
  if (!ast || typeof ast !== 'object') {
    return false;
  }

  // Check the type of the current node
  if ('type' in ast && typeof ast.type === 'string') {
    const dangerousTypes = ['insert', 'update', 'delete', 'drop', 'create', 'alter', 'truncate'];
    if (dangerousTypes.includes(ast.type.toLowerCase())) {
      return true;
    }
  }

  // Recursively check all properties
  for (const key in ast) {
    const value = (ast as Record<string, unknown>)[key];
    
    if (Array.isArray(value)) {
      for (const item of value) {
        if (containsDangerousOperations(item)) {
          return true;
        }
      }
    } else if (typeof value === 'object' && value !== null) {
      if (containsDangerousOperations(value)) {
        return true;
      }
    }
  }

  return false;
}