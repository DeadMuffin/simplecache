# Description: Test cases for the Cache class.
import pytest
import asyncio
import time
import random
from simplecache import Cache

''' Example Database
DB = {}
DB['static_data'] = '{"key": "value", "key2": "value2"}'
DB['dynamic_data_1'] = ...
DB['dynamic_data_2'] = ...
'''



# Mock API routes for testing
@Cache.cache('static_data')
async def mock_get_static_data() -> str:
    """get data from database always with key 'static_data'"""
    await asyncio.sleep(3)
    return "static_data"

@Cache.cache('static_data', invalidate=True)
async def mock_update_static_data() -> None:
    """update data in database always with key 'static_data'"""
    await asyncio.sleep(3)

async def mock_get_dynamic_data(id: str):
    """get data from database with key 'dynamic_data_{id}'"""
    result = Cache.get(key=f'dynamic_data_{id}')
    if result:
        return result
    
    await asyncio.sleep(3)
    data = f"dynamic data {id}"
    Cache.add(key=f'dynamic_data_{id}', value=data, ttl=10)
    
    return data

async def mock_update_dynamic_data_(id: str) -> None:
    """update data in database with key 'dynamic_data_{id}'"""
    
    await asyncio.sleep(3)
    data = f"updated dynamic data {id}"
    Cache.invalidate(key=f'dynamic_data_{id}')



# Fixtures
@pytest.fixture(autouse=True)
def clear_cache_before_each_test():
    """
    Fixture to clear the cache before each test.

    This fixture ensures that the cache is cleared before each test, providing a clean
    state for each test case.
    """
    Cache.clear()

# Testcases
@pytest.mark.asyncio
async def test_get_static_data():
    """
    Testcase 1: Test fetching static data from the cache.

    This test ensures that static data is correctly fetched from the cache.
    The first call populates the cache, and the second call retrieves the data
    from the cache without delay.
    """
    result = await mock_get_static_data()
    assert result == "static_data"
    
    cached_result = Cache.get(key='static_data')
    assert cached_result == "static_data"
    
    start_time = time.time()
    result = await mock_get_static_data()
    end_time = time.time()
    
    assert result == "static_data"
    assert end_time - start_time < 1  # Should be quick due to cache

@pytest.mark.asyncio
async def test_update_static_data():
    """
    Testcase 2: Test updating static data and invalidating the cache.

    This test ensures that static data is correctly updated and that the cache
    is invalidated. After invalidation, the cache should be repopulated on the
    next data fetch.
    """
    await mock_get_static_data()
    
    await mock_update_static_data()
    
    cached_result = Cache.get(key='static_data')
    assert cached_result is None
    
    start_time = time.time()
    result = await mock_get_static_data()
    end_time = time.time()
    
    assert result == "static_data"
    assert end_time - start_time >= 3  # Should take time due to cache miss

@pytest.mark.asyncio
async def test_get_dynamic_data():
    """
    Testcase 3: Test fetching dynamic data from the cache.

    This test ensures that dynamic data is correctly fetched from the cache.
    The first call populates the cache, and the second call retrieves the data
    from the cache without delay.
    """
    dynamic_id = str(random.randint(1, 100))  # Random ID generation
    result = await mock_get_dynamic_data(dynamic_id)
    assert result == f"dynamic data {dynamic_id}"
    
    cached_result = Cache.get(key=f'dynamic_data_{dynamic_id}')
    assert cached_result == f"dynamic data {dynamic_id}"
    
    start_time = time.time()
    result = await mock_get_dynamic_data(dynamic_id)
    end_time = time.time()
    
    assert result == f"dynamic data {dynamic_id}"
    assert end_time - start_time < 1  # Should be quick due to cache

@pytest.mark.asyncio
async def test_update_dynamic_data():
    """
    Testcase 4: Test updating dynamic data and invalidating the cache.

    This test ensures that dynamic data is correctly updated and that the cache
    is invalidated. After invalidation, the cache should be repopulated on the
    next data fetch.
    """
    dynamic_id = str(random.randint(1, 100))  # Random ID generation
    
    await mock_get_dynamic_data(dynamic_id)
    
    await mock_update_dynamic_data_(dynamic_id)
    
    cached_result = Cache.get(key=f'dynamic_data_{dynamic_id}')
    assert cached_result is None
    
    start_time = time.time()
    result = await mock_get_dynamic_data(dynamic_id)
    end_time = time.time()
    
    assert result == f"dynamic data {dynamic_id}"
    assert end_time - start_time >= 3  # Should take time due to cache miss

@pytest.mark.asyncio
async def test_dynamic_data_ttl():
    """
    Testcase 5: Test TTL (Time-to-Live) of dynamic data.

    This test ensures that dynamic data is correctly invalidated after the TTL
    expires. After TTL expiration, the cache should be repopulated on the next
    data fetch.
    """
    dynamic_id = str(random.randint(1, 100))  # Random ID generation
    
    result = await mock_get_dynamic_data(dynamic_id)
    assert result == f"dynamic data {dynamic_id}"
    
    cached_result = Cache.get(key=f'dynamic_data_{dynamic_id}')
    assert cached_result == f"dynamic data {dynamic_id}"
    
    await asyncio.sleep(10)
    
    cached_result = Cache.get(key=f'dynamic_data_{dynamic_id}')
    assert cached_result is None
    
    start_time = time.time()
    result = await mock_get_dynamic_data(dynamic_id)
    end_time = time.time()
    
    assert result == f"dynamic data {dynamic_id}"
    assert end_time - start_time >= 3  # Should take time due to cache miss


# Run the tests
if __name__ == '__main__':
    pytest.main(['-v', '--tb=native', __file__])