# FastAPI Framework - Agent Context Sections

> Sections to include when generating agent context files for FastAPI projects.

## Architecture Section

```markdown
## FastAPI Architecture

### Project Structure

```
src/{{ package }}/
├── main.py           # FastAPI app and startup
├── api/
│   ├── __init__.py
│   ├── routes/       # Route handlers
│   │   ├── __init__.py
│   │   ├── users.py
│   │   └── items.py
│   └── deps.py       # Dependency injection
├── core/
│   ├── config.py     # Settings (pydantic-settings)
│   └── security.py   # Auth utilities
├── models/           # Pydantic models
│   ├── __init__.py
│   ├── user.py
│   └── item.py
├── services/         # Business logic
│   └── user_service.py
└── db/               # Database (if applicable)
    ├── __init__.py
    └── session.py
```

### Request Flow

```
HTTP Request
    ↓
FastAPI Router
    ↓
Dependencies (auth, db session, etc.)
    ↓
Route Handler
    ↓
Service Layer (business logic)
    ↓
Pydantic Response Model
    ↓
HTTP Response
```
```

## Common Tasks Section

```markdown
## FastAPI Common Tasks

### Adding a New Endpoint

1. Define Pydantic models in `models/`:
   ```python
   from pydantic import BaseModel

   class ItemCreate(BaseModel):
       name: str
       price: float

   class ItemResponse(BaseModel):
       id: int
       name: str
       price: float
   ```

2. Create route handler in `api/routes/`:
   ```python
   from fastapi import APIRouter, Depends, HTTPException

   router = APIRouter(prefix="/items", tags=["items"])

   @router.post("/", response_model=ItemResponse, status_code=201)
   async def create_item(
       item: ItemCreate,
       service: ItemService = Depends(get_item_service)
   ) -> ItemResponse:
       return await service.create(item)
   ```

3. Register router in `main.py`:
   ```python
   from api.routes import items
   app.include_router(items.router)
   ```

4. Add tests in `tests/api/test_items.py`

### Adding Authentication

```python
# core/security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    token = credentials.credentials
    try:
        payload = decode_token(token)
        return await get_user(payload["sub"])
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

# Usage in routes
@router.get("/me")
async def get_profile(user: User = Depends(get_current_user)):
    return user
```

### Adding Background Tasks

```python
from fastapi import BackgroundTasks

@router.post("/notify")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_email, email, "Subject", "Body")
    return {"message": "Notification queued"}
```
```

## Testing Section

```markdown
## FastAPI Testing

### Test Client Setup

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from {{ package }}.main import app

@pytest.fixture
def client():
    """Synchronous test client."""
    return TestClient(app)

@pytest.fixture
async def async_client():
    """Async test client for async endpoints."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
```

### Testing Endpoints

```python
# tests/api/test_items.py
class TestCreateItem:
    def test_create_item_success(self, client):
        """Should create item with valid data."""
        response = client.post(
            "/items/",
            json={"name": "Test Item", "price": 9.99}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Item"
        assert "id" in data

    def test_create_item_invalid_price(self, client):
        """Should reject negative price."""
        response = client.post(
            "/items/",
            json={"name": "Test", "price": -1}
        )

        assert response.status_code == 422
        assert "price" in response.json()["detail"][0]["loc"]
```

### Testing with Dependencies Override

```python
from {{ package }}.api.deps import get_db

def test_with_mock_db(client):
    """Test with mocked database."""
    mock_db = MagicMock()

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.get("/items/")

    assert response.status_code == 200
    app.dependency_overrides.clear()
```

### Testing WebSocket

```python
def test_websocket_connection(client):
    """Test WebSocket endpoint."""
    with client.websocket_connect("/ws") as websocket:
        websocket.send_json({"type": "subscribe", "channel": "updates"})
        data = websocket.receive_json()
        assert data["type"] == "subscribed"
```
```

## Error Handling Section

```markdown
## FastAPI Error Handling

### Exception Handlers

```python
# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

class {{ ProjectName }}Error(Exception):
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code

@app.exception_handler({{ ProjectName }}Error)
async def custom_exception_handler(
    request: Request,
    exc: {{ ProjectName }}Error
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"error": exc.code, "message": exc.message}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    # Log the error
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "message": "An unexpected error occurred"}
    )
```

### HTTPException Usage

```python
from fastapi import HTTPException, status

@router.get("/items/{item_id}")
async def get_item(item_id: int):
    item = await service.get(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found"
        )
    return item
```
```

## Security Section

```markdown
## FastAPI Security

### CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Not ["*"] in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### Request Validation

FastAPI + Pydantic handles most validation automatically:

```python
from pydantic import BaseModel, Field, validator

class UserCreate(BaseModel):
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    password: str = Field(..., min_length=8)
    age: int = Field(..., ge=0, le=150)

    @validator('password')
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase')
        return v
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, credentials: LoginRequest):
    ...
```
```

## Gotchas Section

```markdown
## FastAPI-Specific Gotchas

1. **Async vs Sync endpoints**: Use `async def` only if you're actually awaiting something:
   ```python
   # Good - actually async
   @router.get("/")
   async def get_items():
       return await db.fetch_all(query)

   # Good - sync is fine for CPU-bound
   @router.get("/compute")
   def compute():
       return heavy_cpu_computation()

   # Bad - async without await blocks the event loop
   @router.get("/")
   async def get_items():
       return sync_db_call()  # Blocks!
   ```

2. **Response model filtering**: response_model filters output:
   ```python
   class UserDB(BaseModel):
       id: int
       email: str
       hashed_password: str  # Sensitive!

   class UserResponse(BaseModel):
       id: int
       email: str

   @router.get("/users/{id}", response_model=UserResponse)
   async def get_user(id: int) -> UserDB:
       # hashed_password is automatically excluded from response
       return await db.get_user(id)
   ```

3. **Path parameter order matters**:
   ```python
   # WRONG - "/users/me" matches "/users/{user_id}" first
   @router.get("/users/{user_id}")
   @router.get("/users/me")

   # CORRECT - specific routes before parameterized
   @router.get("/users/me")
   @router.get("/users/{user_id}")
   ```

4. **Dependency caching**: Dependencies are cached per-request by default:
   ```python
   # This function runs ONCE per request, even if used by multiple dependencies
   async def get_db():
       async with SessionLocal() as session:
           yield session
   ```

5. **Background tasks run after response**: Don't rely on them for response data:
   ```python
   @router.post("/")
   async def create_item(background_tasks: BackgroundTasks):
       item = await create_in_db()
       background_tasks.add_task(send_notification)  # Runs AFTER response
       return item  # Response sent before notification
   ```
```
