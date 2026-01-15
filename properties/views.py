from django.shortcuts import render
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.http import JsonResponse
from .models import Property
import json

# Cache the entire view response for 15 minutes (60 * 15 = 900 seconds)
@cache_page(60 * 15)
def property_list(request):
    """
    Returns a list of all properties.
    Response is cached in Redis for 15 minutes.
    """
    properties = Property.objects.all().order_by('-created_at')
    
    # Convert properties to dictionary format
    properties_data = [
        {
            'id': prop.id,
            'title': prop.title,
            'description': prop.description,
            'price': str(prop.price),  # Convert Decimal to string for JSON
            'location': prop.location,
            'created_at': prop.created_at.isoformat(),
        }
        for prop in properties
    ]
    
    return JsonResponse({'properties': properties_data})
