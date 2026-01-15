from django.core.cache import cache
from django_redis import get_redis_connection
import logging
from .models import Property

# Set up logger
logger = logging.getLogger(__name__)


def get_all_properties():
    """
    Retrieve all properties with low-level Redis caching.
    
    Returns:
        QuerySet: All Property objects, cached for 1 hour (3600 seconds)
    """
    # Try to get cached properties
    cached_properties = cache.get('all_properties')
    
    if cached_properties is not None:
        # Return cached queryset
        return cached_properties
    
    # If not in cache, fetch from database
    properties = Property.objects.all()
    
    # Store in cache for 1 hour (3600 seconds)
    cache.set('all_properties', properties, 3600)
    
    return properties


def get_redis_cache_metrics():
    """
    Retrieve and analyze Redis cache hit/miss metrics.
    
    Returns:
        dict: Dictionary containing cache metrics including hits, misses, and hit ratio
    """
    try:
        # Get Redis connection
        redis_client = get_redis_connection("default")
        
        # Get Redis INFO command output
        info = redis_client.info()
        
        # Extract cache statistics
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        
        # Calculate hit ratio (avoid division by zero)
        if hits + misses > 0:
            hit_ratio = hits / (hits + misses)
        else:
            hit_ratio = 0.0
        
        # Create metrics dictionary
        metrics = {
            'keyspace_hits': hits,
            'keyspace_misses': misses,
            'hit_ratio': hit_ratio,
            'total_operations': hits + misses,
            'hit_percentage': round(hit_ratio * 100, 2)
        }
        
        # Log the metrics
        logger.info(f"Redis Cache Metrics - Hits: {hits}, Misses: {misses}, "
                   f"Hit Ratio: {hit_ratio:.2%}, Total Operations: {hits + misses}")
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error retrieving Redis cache metrics: {e}")
        # Return error metrics
        return {
            'error': str(e),
            'keyspace_hits': 0,
            'keyspace_misses': 0,
            'hit_ratio': 0.0,
            'total_operations': 0,
            'hit_percentage': 0.0
        }
