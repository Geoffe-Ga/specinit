# React Framework - Agent Context Sections

> Sections to include when generating agent context files for React projects.

## Architecture Section

```markdown
## React Architecture

### Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── ui/              # Generic UI (Button, Input, Modal)
│   └── features/        # Feature-specific components
├── hooks/               # Custom React hooks
├── pages/               # Page components (for routing)
├── services/            # API calls and external services
├── stores/              # State management (if applicable)
├── types/               # TypeScript type definitions
├── utils/               # Utility functions
└── App.tsx              # Root component
```

### Component Organization

```
components/
├── Button/
│   ├── Button.tsx       # Component implementation
│   ├── Button.test.tsx  # Tests
│   ├── Button.css       # Styles (or .module.css)
│   └── index.ts         # Export
```
```

## Code Style Section

```markdown
## React Code Style

### Functional Components

Always use functional components with hooks:

```tsx
// Good - functional component with TypeScript
interface UserCardProps {
  user: User;
  onSelect?: (user: User) => void;
}

export function UserCard({ user, onSelect }: UserCardProps) {
  const handleClick = useCallback(() => {
    onSelect?.(user);
  }, [user, onSelect]);

  return (
    <div className="user-card" onClick={handleClick}>
      <h3>{user.name}</h3>
      <p>{user.email}</p>
    </div>
  );
}

// Avoid - class components (legacy)
class UserCard extends React.Component { ... }
```

### Hook Rules

```tsx
// Good - hooks at top level
function Component({ id }: Props) {
  const [data, setData] = useState<Data | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData(id).then(setData).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <Spinner />;
  return <DataDisplay data={data} />;
}

// Bad - conditional hooks
function Component({ shouldFetch }: Props) {
  if (shouldFetch) {
    const data = useFetch('/api/data'); // Never do this!
  }
}
```

### Event Handlers

```tsx
// Good - useCallback for handlers passed to children
function Parent() {
  const handleSubmit = useCallback((data: FormData) => {
    api.submit(data);
  }, []);

  return <Form onSubmit={handleSubmit} />;
}

// Good - inline for simple handlers not passed down
function Button() {
  return <button onClick={() => console.log('clicked')}>Click</button>;
}
```
```

## Testing Section

```markdown
## React Testing

### Component Testing

```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { UserCard } from './UserCard';

describe('UserCard', () => {
  const mockUser = { id: '1', name: 'John', email: 'john@example.com' };

  it('renders user information', () => {
    render(<UserCard user={mockUser} />);

    expect(screen.getByText('John')).toBeInTheDocument();
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
  });

  it('calls onSelect when clicked', async () => {
    const handleSelect = vi.fn();
    render(<UserCard user={mockUser} onSelect={handleSelect} />);

    await userEvent.click(screen.getByRole('article'));

    expect(handleSelect).toHaveBeenCalledWith(mockUser);
  });
});
```

### Hook Testing

```tsx
import { renderHook, act } from '@testing-library/react';
import { useCounter } from './useCounter';

describe('useCounter', () => {
  it('increments counter', () => {
    const { result } = renderHook(() => useCounter(0));

    act(() => {
      result.current.increment();
    });

    expect(result.current.count).toBe(1);
  });
});
```

### Testing with Providers

```tsx
// test-utils.tsx
import { render, RenderOptions } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}

export function renderWithProviders(
  ui: React.ReactElement,
  options?: RenderOptions
) {
  return render(ui, { wrapper: createWrapper(), ...options });
}
```

### Mocking API Calls

```tsx
import { rest } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  rest.get('/api/users', (req, res, ctx) => {
    return res(ctx.json([{ id: '1', name: 'John' }]));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

it('loads and displays users', async () => {
  render(<UserList />);

  expect(await screen.findByText('John')).toBeInTheDocument();
});
```
```

## State Management Section

```markdown
## State Management

### When to Use What

| State Type | Solution |
|------------|----------|
| UI state (single component) | `useState` |
| UI state (shared) | Context + `useReducer` |
| Server state | React Query / SWR |
| Complex client state | Zustand / Jotai |
| Form state | React Hook Form |

### Local State

```tsx
function SearchInput() {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 300);

  return (
    <input
      value={query}
      onChange={(e) => setQuery(e.target.value)}
    />
  );
}
```

### Server State (React Query)

```tsx
function UserList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['users'],
    queryFn: () => api.getUsers(),
  });

  if (isLoading) return <Spinner />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <ul>
      {data.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

### Form State (React Hook Form)

```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

function LoginForm() {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('email')} />
      {errors.email && <span>{errors.email.message}</span>}
    </form>
  );
}
```
```

## Performance Section

```markdown
## React Performance

### Memoization

```tsx
// Memo for expensive components that receive same props
const ExpensiveList = React.memo(function ExpensiveList({ items }: Props) {
  return items.map((item) => <ExpensiveItem key={item.id} item={item} />);
});

// useMemo for expensive calculations
function Dashboard({ data }: Props) {
  const statistics = useMemo(() => {
    return calculateStatistics(data); // Expensive
  }, [data]);

  return <StatsDisplay stats={statistics} />;
}

// useCallback for handlers passed to memoized children
function Parent() {
  const handleChange = useCallback((value: string) => {
    // Handle change
  }, []);

  return <MemoizedChild onChange={handleChange} />;
}
```

### Code Splitting

```tsx
import { lazy, Suspense } from 'react';

// Lazy load heavy components
const HeavyChart = lazy(() => import('./HeavyChart'));

function Dashboard() {
  return (
    <Suspense fallback={<Spinner />}>
      <HeavyChart data={data} />
    </Suspense>
  );
}
```

### Avoid Re-renders

```tsx
// Bad - creates new object every render
<Component style={{ color: 'red' }} />

// Good - stable reference
const style = { color: 'red' };
<Component style={style} />

// Good - useMemo for computed styles
const style = useMemo(() => ({
  color: isActive ? 'blue' : 'gray'
}), [isActive]);
```
```

## Security Section

```markdown
## React Security

### XSS Prevention

```tsx
// Safe - React escapes by default
<div>{userInput}</div>

// Dangerous - only use with sanitized content
<div dangerouslySetInnerHTML={{ __html: sanitizedHtml }} />

// If you must use dangerouslySetInnerHTML:
import DOMPurify from 'dompurify';
const sanitized = DOMPurify.sanitize(untrustedHtml);
<div dangerouslySetInnerHTML={{ __html: sanitized }} />
```

### Sensitive Data

```tsx
// Never put secrets in frontend code
const API_KEY = 'secret'; // WRONG - bundled into JS

// Use environment variables (still visible in bundle)
const API_URL = import.meta.env.VITE_API_URL; // Public config only

// Sensitive operations should go through your backend
async function createPayment(amount: number) {
  // Backend handles the actual API key
  return api.post('/payments', { amount });
}
```

### URL Handling

```tsx
// Validate URLs before using
function SafeLink({ href, children }: Props) {
  const isValid = href.startsWith('https://') || href.startsWith('/');

  if (!isValid) {
    console.warn('Invalid href blocked:', href);
    return <span>{children}</span>;
  }

  return <a href={href}>{children}</a>;
}
```
```

## Gotchas Section

```markdown
## React-Specific Gotchas

1. **Stale closures in useEffect**:
   ```tsx
   // Bug - count is stale
   useEffect(() => {
     const interval = setInterval(() => {
       setCount(count + 1); // Always uses initial count
     }, 1000);
     return () => clearInterval(interval);
   }, []); // Empty deps

   // Fix - use functional update
   useEffect(() => {
     const interval = setInterval(() => {
       setCount((c) => c + 1); // Uses latest value
     }, 1000);
     return () => clearInterval(interval);
   }, []);
   ```

2. **Object/array dependencies**:
   ```tsx
   // Bug - new object every render triggers effect
   useEffect(() => {
     fetchData(options);
   }, [{ page, limit }]); // New object each render!

   // Fix - primitive dependencies
   useEffect(() => {
     fetchData({ page, limit });
   }, [page, limit]);
   ```

3. **setState is async**:
   ```tsx
   // Bug - reading stale state
   setCount(count + 1);
   console.log(count); // Still old value!

   // Fix - use effect for side effects after state update
   useEffect(() => {
     console.log(count); // New value
   }, [count]);
   ```

4. **Keys on lists**:
   ```tsx
   // Bug - index as key causes issues on reorder
   {items.map((item, index) => (
     <Item key={index} item={item} /> // Bad with dynamic lists
   ))}

   // Fix - stable unique key
   {items.map((item) => (
     <Item key={item.id} item={item} />
   ))}
   ```

5. **Context re-renders**:
   ```tsx
   // Problem - all consumers re-render on any change
   const value = { user, settings, theme };
   return <Context.Provider value={value}>{children}</Context.Provider>;

   // Fix - split contexts or memoize value
   const value = useMemo(() => ({ user, settings, theme }), [user, settings, theme]);
   ```
```
