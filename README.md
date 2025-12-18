# python-ai-utils

**Async utilities for building reliable AI API clients in Python.**

A production-ready toolkit for working with AI APIs (OpenAI, Anthropic, etc.) that handles the hard parts: retries, rate limiting, timeouts, and structured logging.

---

## 🎯 Why This Library?

Building AI applications isn't just about calling models. You need:

- ✅ **Reliable requests** with automatic retries and exponential backoff
- ✅ **Rate limiting** to avoid hitting API quotas
- ✅ **Timeouts** to prevent hanging requests
- ✅ **Structured logging** for production debugging
- ✅ **Type safety** with full type hints

This library provides all of that in a clean, reusable package.

---

## 🚀 Features

### Core Components

- **`AsyncAPIClient`** - Production-ready async HTTP client with:
  - Automatic retries with exponential backoff
  - Configurable timeouts
  - Rate limiting
  - Connection pooling
  - Structured logging

- **Decorators** - Composable utilities:
  - `@timeout` - Add timeout to any async function
  - `@retry` - Automatic retries with backoff
  - `@measure_time` - Track execution time

- **`RateLimiter`** - Control request frequency:
  - Token bucket algorithm
  - Semaphore-based limiting
  - Async-safe

- **`StructuredLogger`** - JSON logs for production:
  - Request tracing with IDs
  - Latency tracking
  - ELK/DataDog ready

---

## 📦 Installation

```bash
pip install -r requirements.txt
```

---

## 🔥 Quick Start

### Basic Usage

```python
import asyncio
from ai_utils import AsyncAPIClient

async def main():
    async with AsyncAPIClient(
        base_url="https://api.example.com",
        timeout=10.0,
        max_retries=3
    ) as client:
        # GET request
        data = await client.get("/endpoint")
        
        # POST with JSON
        response = await client.post(
            "/chat",
            json={"message": "Hello!"}
        )

asyncio.run(main())
```

### With Rate Limiting

```python
async with AsyncAPIClient(
    base_url="https://api.example.com",
    rate_limit=10  # Max 10 requests per second
) as client:
    # Make concurrent requests safely
    tasks = [client.get(f"/item/{i}") for i in range(50)]
    results = await asyncio.gather(*tasks)
```

### Using Decorators Standalone

```python
from ai_utils.decorators import timeout, retry, measure_time

@retry(max_retries=3, backoff="exponential")
@measure_time
@timeout(seconds=5)
async def fetch_data(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

---

## 📚 Examples

See the [`examples/`](examples/) directory for complete examples:

- [`basic_usage.py`](examples/basic_usage.py) - Simple GET/POST requests
- [`with_retries.py`](examples/with_retries.py) - Handling failures and timeouts
- [`with_rate_limiting.py`](examples/with_rate_limiting.py) - Concurrent requests with rate limiting
- [`decorators_standalone.py`](examples/decorators_standalone.py) - Using decorators independently
- [`structured_logging.py`](examples/structured_logging.py) - Production-ready logging

Run any example:

```bash
python examples/basic_usage.py
```

---

## 🏗️ Architecture

### Project Structure

```
python-ai-utils/
├── ai_utils/
│   ├── __init__.py           # Public API
│   ├── client.py             # AsyncAPIClient
│   ├── rate_limit.py         # RateLimiter
│   ├── logging.py            # StructuredLogger
│   └── decorators/
│       ├── __init__.py
│       ├── timeout.py        # @timeout decorator
│       ├── retry.py          # @retry decorator
│       └── timing.py         # @measure_time decorator
│
├── examples/                 # Usage examples
├── main.py                   # Original prototype code
├── requirements.txt
└── README.md
```

### Design Principles

1. **Async-first**: Built on `asyncio` and `aiohttp` for high performance
2. **Composable**: Use components independently or together
3. **Production-ready**: Logging, error handling, and retry logic included
4. **Type-safe**: Full type hints for better IDE support
5. **Testable**: Modular design for easy unit testing

---

## 🔧 API Reference

### AsyncAPIClient

```python
client = AsyncAPIClient(
    base_url: str = "",                    # Base URL for all requests
    timeout: float = 30.0,                 # Default timeout in seconds
    max_retries: int = 3,                  # Max retry attempts
    rate_limit: Optional[int] = None,      # Requests per second
    headers: Optional[Dict[str, str]] = None,  # Default headers
    enable_logging: bool = True            # Enable structured logging
)

# HTTP methods
await client.get(endpoint, **kwargs)
await client.post(endpoint, **kwargs)
await client.put(endpoint, **kwargs)
await client.delete(endpoint, **kwargs)
await client.patch(endpoint, **kwargs)
```

### Decorators

```python
@timeout(seconds: float)
# Timeout for async functions

@retry(max_retries: int = 3, backoff: str = "exponential")
# Automatic retries with backoff ("exponential" or "linear")

@measure_time
# Measure and log execution time
```

### RateLimiter

```python
limiter = RateLimiter(
    max_requests: int,           # Maximum requests allowed
    time_window: float = 1.0,    # Time window in seconds
    mode: str = "token_bucket"   # "token_bucket" or "semaphore"
)

async with limiter:
    # Your API call here
    await client.request(...)
```

### StructuredLogger

```python
logger = StructuredLogger(name: str = "ai_utils", level: int = logging.INFO)

logger.log_request(request_id, url, method, status, latency_ms, error)
logger.log_retry(request_id, attempt, max_attempts, error, delay_seconds)
logger.info(message, **extra)
logger.warning(message, **extra)
logger.error(message, **extra)
```

---

## 🛠️ Development Roadmap

### Week 1-2: Foundation ✅ (Current)
- ✅ Async client with retries
- ✅ Rate limiting
- ✅ Timeouts
- ✅ Structured logging

### Week 3-4: AI Integration (Planned)
- [ ] OpenAI API wrapper
- [ ] Anthropic API wrapper
- [ ] Streaming support
- [ ] Token counting

### Month 2-3: Advanced Features (Future)
- [ ] Response caching
- [ ] Batch processing
- [ ] Circuit breaker pattern
- [ ] Metrics collection

### Month 4+: Production Tools (Future)
- [ ] RAG utilities
- [ ] Agent frameworks
- [ ] Prompt templates
- [ ] Cost tracking

---

## 🤝 Contributing

This is a learning project and part of an AI Engineering roadmap. Feedback and suggestions are welcome!

---

## 📄 License

MIT License - feel free to use this in your projects.

---

## 🎓 Learning Path

This library is part of a structured AI Engineering learning path:

**Week 1**: Async fundamentals, retries, rate limiting, timeouts  
**Week 2-3**: AI API integration (OpenAI, Anthropic)  
**Month 2**: RAG systems and vector databases  
**Month 3**: Agent frameworks and tool calling  
**Month 4**: Production deployment

> **Goal**: Build production-grade AI systems, not just call APIs.

---

## 📞 Questions?

This library demonstrates:
- Professional Python async patterns
- Production-ready error handling
- Scalable API client architecture
- Engineering best practices for AI systems

