#!/usr/bin/env python
"""
Test script to verify property list caching.
"""
import os
import django
import time
import requests
from django.core.cache import cache

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alxbackendcachingpropertylistings.settings')
django.setup()

print("=" * 60)
print("Testing Property List Caching")
print("=" * 60)

# First, let's create some test data
from properties.models import Property

print("\n1. Creating test properties...")
# Clear existing test data
Property.objects.all().delete()

# Create test properties
properties_data = [
    {
        'title': 'Modern Apartment',
        'description': 'Beautiful apartment in city center',
        'price': 250000.00,
        'location': 'New York'
    },
    {
        'title': 'Lakeside Cottage',
        'description': 'Cozy cottage with lake view',
        'price': 150000.00,
        'location': 'Michigan'
    },
    {
        'title': 'Beach House',
        'description': 'Beachfront property with ocean view',
        'price': 750000.00,
        'location': 'California'
    }
]

for data in properties_data:
    Property.objects.create(**data)

print(f"   Created {Property.objects.count()} properties")

# Start Django server in background or use test client
from django.test import Client

print("\n2. Testing property list endpoint...")
client = Client()

# First request (should hit database)
print("   Making first request (uncached)...")
start_time = time.time()
response1 = client.get('/properties/')
end_time = time.time()
print(f"   Response time: {end_time - start_time:.3f} seconds")
print(f"   Status code: {response1.status_code}")
print(f"   Number of properties in response: {len(response1.json())}")

# Second request (should come from cache)
print("\n   Making second request (should be cached)...")
start_time = time.time()
response2 = client.get('/properties/')
end_time = time.time()
print(f"   Response time: {end_time - start_time:.3f} seconds")
print(f"   Status code: {response2.status_code}")

# Verify cache is working
if (end_time - start_time) < 0.01:  # Cached responses are very fast
    print("   ✅ Response served from cache (fast response time)")
else:
    print("   ❌ Response may not be cached (slow response time)")

# Check Redis cache directly
print("\n3. Checking Redis cache directly...")
cache_key = None

# Find the cache key (Django cache_page creates specific keys)
from django.utils.http import http_date
from django.utils.cache import get_cache_key

# Try to get cache key
try:
    request = client.request().wsgi_request
    request.path = '/properties/'
    request.method = 'GET'
    
    # Generate cache key
    cache_key = get_cache_key(request)
    if cache_key:
        print(f"   Cache key found: {cache_key[:50]}...")
        
        # Check if data is in cache
        cached_data = cache.get(cache_key)
        if cached_data:
            print("   ✅ Data found in Redis cache")
        else:
            print("   ❌ No data found in Redis cache for this key")
    else:
        print("   ⚠️  Could not generate cache key")
except Exception as e:
    print(f"   ⚠️  Could not check cache directly: {e}")

# Test cache expiration
print("\n4. Testing cache headers...")
# Check cache-control headers
if 'Cache-Control' in response2:
    cache_control = response2['Cache-Control']
    print(f"   Cache-Control header: {cache_control}")
    if 'max-age=900' in cache_control or 'max-age=900,' in cache_control:
        print("   ✅ Cache set for 15 minutes (900 seconds)")
    else:
        print("   ❌ Cache duration not set to 15 minutes")

# Test with different query parameters
print("\n5. Testing with different URLs...")
response3 = client.get('/properties/?format=json')
print(f"   Response for /properties/?format=json: {response3.status_code}")

print("\n" + "=" * 60)
print("Caching test complete!")
print("=" * 60)

# Clean up
Property.objects.all().delete()
