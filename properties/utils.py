from django.core.cache import cache
from .models import Property


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
