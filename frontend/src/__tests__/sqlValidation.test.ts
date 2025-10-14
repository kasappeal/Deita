import { validateSqlSyntax } from '../utils/sqlValidation';

describe('validateSqlSyntax', () => {
  it('should validate empty query', () => {
    const result = validateSqlSyntax('');
    expect(result.isValid).toBe(false);
    expect(result.error).toBe('Query cannot be empty');
  });

  it('should validate whitespace-only query', () => {
    const result = validateSqlSyntax('   ');
    expect(result.isValid).toBe(false);
    expect(result.error).toBe('Query cannot be empty');
  });

  it('should reject non-SELECT queries', () => {
    const result = validateSqlSyntax('INSERT INTO users VALUES (1)');
    expect(result.isValid).toBe(false);
    expect(result.error).toContain('Only SELECT queries are allowed');
  });

  it('should validate basic SELECT query', () => {
    const result = validateSqlSyntax('SELECT * FROM users');
    expect(result.isValid).toBe(true);
  });

  it('should allow SELECT without FROM clause', () => {
    // SELECT without FROM is valid in PostgreSQL (e.g., SELECT 1, SELECT NOW())
    const result = validateSqlSyntax('SELECT 1');
    expect(result.isValid).toBe(true);
  });

  it('should reject unbalanced parentheses', () => {
    const result = validateSqlSyntax('SELECT * FROM users WHERE id = (1');
    expect(result.isValid).toBe(false);
    // Parser will detect syntax error
    expect(result.error).toBeDefined();
  });

  it('should reject unbalanced single quotes', () => {
    const result = validateSqlSyntax("SELECT * FROM users WHERE name = 'john");
    expect(result.isValid).toBe(false);
    // Parser will detect syntax error
    expect(result.error).toBeDefined();
  });

  it('should reject unbalanced double quotes', () => {
    const result = validateSqlSyntax('SELECT * FROM users WHERE name = "john');
    expect(result.isValid).toBe(false);
    // Parser will detect syntax error
    expect(result.error).toBeDefined();
  });

  it('should reject dangerous SQL operations', () => {
    const dangerousQueries = [
      { query: 'DROP TABLE users', expectedError: 'Only SELECT queries are allowed' },
      { query: 'DELETE FROM users', expectedError: 'Only SELECT queries are allowed' },
      { query: 'UPDATE users SET name = "hacked"', expectedError: 'Only SELECT queries are allowed' },
      { query: 'INSERT INTO users VALUES (1)', expectedError: 'Only SELECT queries are allowed' },
      { query: 'ALTER TABLE users ADD COLUMN password VARCHAR(255)', expectedError: 'Only SELECT queries are allowed' },
      { query: 'CREATE TABLE new_table (id INT)', expectedError: 'Only SELECT queries are allowed' },
      { query: 'SELECT * FROM users; DROP TABLE users;', expectedError: 'Multiple SQL statements are not allowed' }
    ];

    dangerousQueries.forEach(({ query, expectedError }) => {
      const result = validateSqlSyntax(query);
      expect(result.isValid).toBe(false);
      expect(result.error).toContain(expectedError);
    });
  });

  it('should reject incomplete statements', () => {
    const incompleteQueries = [
      'SELECT * FROM',
      'SELECT * FROM users WHERE',
      'SELECT * FROM users ORDER',
      'SELECT * FROM users GROUP',
      'SELECT * FROM users HAVING',
      'SELECT * FROM users JOIN'
    ];

    incompleteQueries.forEach(query => {
      const result = validateSqlSyntax(query);
      expect(result.isValid).toBe(false);
      // Parser will throw a syntax error for incomplete queries
      expect(result.error).toBeDefined();
    });
  });

  it('should validate complex valid queries', () => {
    const validQueries = [
      'SELECT id, name FROM users WHERE age > 18 ORDER BY name',
      'SELECT u.name, p.title FROM users u JOIN posts p ON u.id = p.user_id',
      'SELECT COUNT(*) as total FROM users GROUP BY status HAVING COUNT(*) > 1',
      "SELECT * FROM users WHERE name LIKE '%john%'",
      'SELECT DISTINCT category FROM products ORDER BY category',
      // Test the specific case from the issue
      'SELECT shipping_country, COUNT(*) AS order_count FROM orders GROUP BY shipping_country ORDER BY order_count DESC LIMIT 1',
      'SELECT shipping_country, COUNT(*) AS order_count FROM orders GROUP BY shipping_country ORDER BY order_count DESC LIMIT 1;'
    ];

    validQueries.forEach(query => {
      const result = validateSqlSyntax(query);
      expect(result.isValid).toBe(true);
    });
  });
});