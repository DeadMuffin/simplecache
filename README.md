# Simple Cache Decorator for Async Functions

This Python module provides a simple cache decorator for async functions, allowing developers to efficiently cache the results of asynchronous function calls.

## Features

- **Asynchronous Support**: Compatible with async functions in Python, allowing caching of asynchronous operations.
- **Time-to-Live (TTL)**: Cache entries can have an expiration time set by the TTL parameter, ensuring cache freshness.
- **Cache Invalidation**: Supports cache invalidation for both static and dynamic data, allowing developers to force data refresh when needed.
- **Logging**: Provides basic logging functionality to track cache hits, misses, and invalidations.
- **Customizable**: Developers can customize cache behavior with options such as ignoring the cache or invalidating it before function execution.

## Usage

To use the cache decorator, simply import the `Cache` class and apply the `@Cache.cache` decorator to your async functions with static keys or use the `Cache.add`, `Cache.get` and `Cache.invalidate` functions for dynamic Arguments.
Here's an example:

```python
    import asyncio
    from cache import Cache

    @Cache.cache(key='static_function', ttl=10)
    async def static_function() -> str:
        await asyncio.sleep(5)
        return 'static_function'

    @Cache.cache(key='static_function',invalidate=True)
    async def invalidate_static_cache():
        # do some stuff
        await asyncio.sleep(3)
        
    async def dynamic_function(id: str) -> str:
        # retrieve if in cache
        cached = Cache.get(key=f'dynamic_function_{id}')
        if cached:
            return cached
        
        # do some stuff
        await asyncio.sleep(5)

        # Add to cache
        Cache.add(key=f'dynamic_function_{id}', value=f'dynamic_function_{id}', ttl=2)
        
        return f'dynamic_function_{id}'

    async def invalidate_dynamic_cache(id: str):
        # do some stuff
        # update DB, etc

        Cache.invalidate(key=f'dynamic_function_{id}')
```


## Installation

1. Clone the repository:

```
git clone https://github.com/DeadMuffin/simplecache.git
```

2. Navigate to the directory:

```
cd simplecache
```

3. Start using the cache decorator in your Python projects.

4. When Testing install *test_requirements.txt*
```bash
    pip install test_requirements.txt
```

## Testing

This module comes with a comprehensive set of test cases to ensure its correctness. To run the tests, execute the following command:

```
pytest -v --tb=native cachetest.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
