from django.views.decorators.cache import cache_page
from django.http import JsonResponse
from .utils import get_all_properties


@cache_page(60 * 15)
def property_list(request):
    """
    Returns a list of all properties.
    Uses low-level caching for the queryset and page-level caching for response.
    """
    # Use the utility function that implements low-level caching
    properties = get_all_properties()
    
    # Convert to list of dictionaries for JSON response
    properties_data = list(properties.values())
    
    return JsonResponse({'properties': properties_data})
