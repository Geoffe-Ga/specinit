# TypeScript - Agent Context Sections

> Sections to include when generating agent context files for TypeScript/JavaScript projects.

## Quick Start Section

```markdown
## Quick Start

```bash
# Install dependencies
{{ package_manager }} install

# Run development server
{{ package_manager }} run dev

# Run tests
{{ package_manager }} test

# Run linting
{{ package_manager }} run lint

# Type check
{{ package_manager }} run typecheck
```
```

## Code Style Section

```markdown
## Code Style

### Formatting & Linting

- **Formatter**: Prettier
- **Linter**: ESLint with TypeScript rules
- **Type checker**: TypeScript strict mode

### Type Definitions

Always use explicit types for function signatures:

```typescript
// Good - explicit types
function processData(items: string[], limit: number = 10): Record<string, number> {
  // ...
}

// Good - interface for complex types
interface ProcessOptions {
  limit?: number;
  filter?: (item: string) => boolean;
}

function processData(items: string[], options?: ProcessOptions): Result {
  // ...
}

// Avoid - implicit any
function processData(items, options) {
  // ...
}
```

### Prefer Interfaces Over Types

```typescript
// Preferred for object shapes
interface User {
  id: string;
  name: string;
  email: string;
}

// Use type for unions, intersections, primitives
type Status = 'pending' | 'active' | 'completed';
type ID = string | number;
```

### Async/Await

```typescript
// Good - async/await with proper error handling
async function fetchData(id: string): Promise<Data> {
  try {
    const response = await api.get(`/data/${id}`);
    return response.data;
  } catch (error) {
    if (error instanceof NotFoundError) {
      throw new DataNotFoundError(`Data ${id} not found`);
    }
    throw error;
  }
}

// Avoid - unhandled promise
function fetchData(id: string) {
  api.get(`/data/${id}`); // Missing await and return
}
```
```

## Testing Section

```markdown
## Testing Conventions

### Test File Naming

```
src/utils/helper.ts     →  src/utils/helper.test.ts
src/components/Button.tsx  →  src/components/Button.test.tsx
```

### Test Structure

```typescript
import { describe, it, expect, beforeEach } from '{{ test_framework }}';
import { functionUnderTest } from './module';

describe('functionUnderTest', () => {
  let testData: TestData;

  beforeEach(() => {
    testData = createTestData();
  });

  it('should return expected result for valid input', () => {
    const result = functionUnderTest(testData);
    expect(result).toEqual(expectedValue);
  });

  it('should handle edge cases gracefully', () => {
    const result = functionUnderTest([]);
    expect(result).toBeNull();
  });

  it('should throw for invalid input', () => {
    expect(() => functionUnderTest(null)).toThrow('Input required');
  });
});
```

### Mocking

```typescript
import { vi } from 'vitest';  // or jest.fn() for Jest

// Mock a module
vi.mock('./api', () => ({
  fetchData: vi.fn().mockResolvedValue({ id: '1', name: 'Test' }),
}));

// Mock a specific function
const mockFn = vi.fn().mockReturnValue('mocked');

// Verify calls
expect(mockFn).toHaveBeenCalledWith(expectedArg);
expect(mockFn).toHaveBeenCalledTimes(1);
```
```

## Error Handling Section

```markdown
## Error Handling

### Custom Error Classes

```typescript
// src/errors.ts
export class {{ ProjectName }}Error extends Error {
  constructor(message: string) {
    super(message);
    this.name = '{{ ProjectName }}Error';
  }
}

export class ValidationError extends {{ ProjectName }}Error {
  constructor(
    message: string,
    public field: string,
    public value: unknown
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}

export class NotFoundError extends {{ ProjectName }}Error {
  constructor(resource: string, id: string) {
    super(`${resource} with id ${id} not found`);
    this.name = 'NotFoundError';
  }
}
```

### Error Handling Patterns

```typescript
// Good - specific error handling
try {
  const data = await fetchResource(id);
  return processData(data);
} catch (error) {
  if (error instanceof NotFoundError) {
    return null; // Expected case
  }
  if (error instanceof ValidationError) {
    logger.warn('Validation failed', { field: error.field });
    throw error; // Re-throw for caller
  }
  // Unexpected error - log and re-throw
  logger.error('Unexpected error', { error });
  throw error;
}

// Bad - swallowing errors
try {
  await riskyOperation();
} catch {
  // Silent failure - never do this
}
```

### Result Type Pattern

```typescript
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E };

function parseConfig(input: string): Result<Config, ValidationError> {
  try {
    const config = JSON.parse(input);
    return { success: true, data: validateConfig(config) };
  } catch (error) {
    return {
      success: false,
      error: new ValidationError('Invalid config format', 'config', input)
    };
  }
}
```
```

## Security Section

```markdown
## Security Considerations

### Input Validation

```typescript
import { z } from 'zod';  // or similar validation library

// Define schema
const UserInputSchema = z.object({
  name: z.string().min(1).max(100).regex(/^[\w\s-]+$/),
  email: z.string().email(),
  age: z.number().int().min(0).max(150).optional(),
});

// Validate input
function processUserInput(input: unknown): UserInput {
  return UserInputSchema.parse(input);
}
```

### XSS Prevention

```typescript
// WRONG - direct HTML injection
element.innerHTML = userInput;

// CORRECT - use textContent for plain text
element.textContent = userInput;

// CORRECT - use framework's escaping (React, Vue, etc.)
return <div>{userInput}</div>;  // React auto-escapes

// CORRECT - sanitize if HTML is needed
import DOMPurify from 'dompurify';
element.innerHTML = DOMPurify.sanitize(userInput);
```

### Environment Variables

```typescript
// CORRECT - validate env vars at startup
const config = {
  apiUrl: process.env.API_URL ?? throwError('API_URL required'),
  apiKey: process.env.API_KEY ?? throwError('API_KEY required'),
};

// CORRECT - type-safe env access
import { z } from 'zod';

const envSchema = z.object({
  API_URL: z.string().url(),
  API_KEY: z.string().min(1),
  NODE_ENV: z.enum(['development', 'production', 'test']),
});

export const env = envSchema.parse(process.env);
```
```

## Dependencies Section

```markdown
## Dependencies

### Adding Dependencies

```bash
# Runtime dependency
{{ package_manager }} add package-name

# Development dependency
{{ package_manager }} add -D package-name
```

### Import Organization

```typescript
// 1. Node built-ins
import { readFile } from 'fs/promises';
import path from 'path';

// 2. External packages
import express from 'express';
import { z } from 'zod';

// 3. Internal aliases (@/)
import { config } from '@/config';
import { logger } from '@/utils/logger';

// 4. Relative imports
import { helper } from './helper';
import type { Options } from './types';
```
```

## Gotchas Section

```markdown
## TypeScript-Specific Gotchas

1. **Type narrowing with `in` operator**:
   ```typescript
   // Use 'in' for type guards
   if ('error' in response) {
     // TypeScript knows response has error property
     console.error(response.error);
   }
   ```

2. **Async function return types**:
   ```typescript
   // Function returns Promise<void>, not void
   async function doSomething(): Promise<void> {
     await someAsyncOp();
   }
   ```

3. **Object.keys returns string[]**:
   ```typescript
   const obj = { a: 1, b: 2 };
   // Object.keys returns string[], not (keyof typeof obj)[]
   Object.keys(obj).forEach((key) => {
     // key is string, need assertion
     console.log(obj[key as keyof typeof obj]);
   });

   // Better: use Object.entries
   Object.entries(obj).forEach(([key, value]) => {
     console.log(key, value);
   });
   ```

4. **Nullish coalescing vs OR**:
   ```typescript
   // ?? only checks null/undefined
   const value = input ?? 'default';  // '' stays as ''

   // || checks all falsy values
   const value = input || 'default';  // '' becomes 'default'
   ```

5. **Satisfies operator for type checking**:
   ```typescript
   // Preserves literal types while checking shape
   const config = {
     endpoint: '/api',
     timeout: 5000,
   } satisfies Config;
   // typeof config.endpoint is '/api', not string
   ```
```
