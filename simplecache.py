# Description: Simple cache decorator for async functions
from functools import wraps
from typing import Awaitable, Callable, TypeVar, ParamSpec, Any, Dict
import logging
import time


_P = ParamSpec('_P')
_T = TypeVar('_T')
logger = logging.getLogger(__name__)

class Cache:
    """
    Simple cache decorator for async functions.

    Example usage:
    ```
    import asyncio

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
        
    @Cache.cache(key='static_function', ttl=10)
    async def static_function() -> str:
        await asyncio.sleep(5)
        return 'static_function'

    @Cache.cache(key='static_function',invalidate=True)
    async def invalidate_static_cache():
        # do some stuff
        await asyncio.sleep(3)
        

    async def invalidate_dynamic_cache(id: str):
        # do some stuff
        # update DB, etc

        Cache.invalidate(key=f'dynamic_function_{id}')
    ```

    """
    _cache: Dict[str, Any] = {}
    _ttl: Dict[str, float] = {}

    @classmethod
    def cache(cls, key: str, ttl: float = 3600, ignore: bool = False, invalidate: bool = False) -> Callable[[Callable[_P, Awaitable[_T]]], Callable[_P, Awaitable[_T]]]:
        """
        Decorator to cache the results of an async function. Can only cache functions with no arguments.

        Args:
            key (str): The cache key.
            ttl (float, optional): Time-to-live for the cache entry in seconds. Defaults to 3600.
            ignore (bool, optional): If True, ignore the cache and always execute the function. Defaults to False.
            invalidate (bool, optional): If True, invalidate the cache entry before executing the function. Defaults to False.

        Returns:
            Callable[[Callable[_P, Awaitable[_T]]], Callable[_P, Awaitable[_T]]]: Decorated function.
        """
        def decorator(func: Callable[_P, Awaitable[_T]]) -> Callable[_P, Awaitable[_T]]:
            
            @wraps(func)
            async def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T:
                t: float = time.time()
                
                if invalidate and key in cls._cache:
                    cls._ttl[key] = t - 60
                    logger.info(f'Cache invalidated for {key}')
                    return await func(*args, **kwargs)

                if not ignore and key in cls._cache:
                    if cls._ttl[key] > t:
                        logger.info(f'Cache hit for {key}')
                        return cls._cache[key]
                    
                logger.info(f'Cache miss for {key}')
                result = await func(*args, **kwargs)
                cls._cache[key] = result
                cls._ttl[key] = t + ttl
                logger.info(f'Cache set for {key} valid until {time.strftime("%H:%M:%S", time.gmtime(t + ttl))} UTC')
                return result
            return wrapper
        return decorator
    
    @classmethod
    def add(cls, key: str, value: Any, ttl: float = 3600) -> None:
        """
        Add a value to the cache with the specified key.

        Args:
            key (str): The cache key.
            value (Any): The value to be cached.
            ttl (float, optional): Time-to-live for the cache entry in seconds. Defaults to 3600.
        """
        t: float = time.time()
        cls._cache[key] = value
        cls._ttl[key] = t + ttl
        logger.info(f'Cache set for {key} valid until {time.strftime("%H:%M:%S", time.gmtime(t + ttl))} UTC')
    
    @classmethod
    def get(cls, key: str) -> Any:
        """
        Get a value from the cache.

        Args:
            key (str): The cache key.

        Returns:
            Any: The cached value, or None if not found or expired.
        """
        t: float = time.time()
        if key in cls._cache:
            if cls._ttl[key] > t:
                logger.info(f'Cache hit for {key}')
                return cls._cache[key]
        logger.info(f'Cache miss for {key}')
        return None
    
    @classmethod
    def invalidate(cls, key: str) -> None:
        """
        Invalidate a cache entry.

        Args:
            key (str): The cache key.
        """
        if key in cls._cache:
            cls._ttl[key] = time.time() - 60
            logger.info(f'Cache invalidated for {key}')

    @classmethod
    def clear(cls) -> None:
        """
        Clear the entire cache.
        """
        cls._cache = {}
        cls._ttl = {}
        logger.info('Cache cleared')
