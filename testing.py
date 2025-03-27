# To handle pagination, caching, and error handling in your Django view and utility function, here's an updated implementation:



### Step 1: Update the Utility Function (utils.py)

# The utility function will now handle pagination by making multiple requests if there are additional pages. It will also include caching and improved error handling.

# python
import requests
from django.core.cache import cache
from requests.exceptions import RequestException

def fetch_settlements(page=1):
    url = "https://api.heartlandev.com.ng/wallet/verify/settlements/"
    params = {"page": page}  # Add pagination parameter
    cache_key = f"settlements_page_{page}"  # Unique cache key for each page

    # Check if data is already cached
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        # Cache the response for 5 minutes (300 seconds)
        cache.set(cache_key, data, timeout=300)
        return data
    except RequestException as e:
        # Handle specific HTTP errors
        if response.status_code == 404:
            print(f"Error: Resource not found (404) - {e}")
        elif response.status_code == 500:
            print(f"Error: Server error (500) - {e}")
        else:
            print(f"Error fetching settlements: {e}")
        return None




### Step 2: Update the Django View (views.py)

# The view will now handle pagination by fetching all pages of data and combining the results. It will also handle caching and errors gracefully.

# python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import fetch_settlements  # Import the utility function

class SettlementView(APIView):
    def get(self, request, *args, **kwargs):
        all_results = []
        page = 1

        while True:
            # Fetch data for the current page
            settlements_data = fetch_settlements(page=page)
            
            if not settlements_data:
                # If no data is returned, return an error response
                return Response(
                    {"error": "Unable to fetch settlements data"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Add the results to the combined list
            all_results.extend(settlements_data.get("results", []))

            # Check if there is a next page
            if not settlements_data.get("next"):
                break  # Exit the loop if there are no more pages

            page += 1  # Move to the next page

        # Return the combined results
        return Response(
            {
                "count": len(all_results),
                "results": all_results,
            },
            status=status.HTTP_200_OK
        )




### Step 3: Update urls.py

# No changes are needed here unless you want to add additional endpoints for pagination.

# python
from django.urls import path
# from .views import SettlementView  # Import the view

urlpatterns = [
    path('settlements/', SettlementView.as_view(), name='settlements'),
]




### Step 4: Configure Caching in settings.py

# To enable caching, configure a cache backend in your Django settings.py. For example, you can use the local memory cache for development:

# python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-settlements-cache',
    }
}


# For production, consider using a more robust cache backend like Redis or Memcached.



### Explanation of Changes

# 1. *Pagination*:
#    - The utility function now accepts a page parameter to fetch data for a specific page.
#    - The view fetches all pages by looping until there are no more pages (next is null).

# 2. *Caching*:
#    - Each page's data is cached using a unique key (settlements_page_{page}).
#    - The cache is set to expire after 5 minutes (300 seconds). You can adjust this timeout as needed.

# 3. *Error Handling*:
#    - Specific HTTP errors (e.g., 404, 500) are handled and logged.
#    - If the utility function fails to fetch data, the view returns a 500 error response.

# ---

### Step 5: Test the Implementation

# 1. Run your Django development server:
#    bash
#    python manage.py runserver
   

# 2. Visit the endpoint (e.g., http://127.0.0.1:8000/settlements/) in your browser or use a tool like Postman to test the API.

# 3. Verify that:
#    - All pages of data are fetched and combined.
#    - Data is cached and reused for subsequent requests within the cache timeout.
#    - Errors are handled gracefully.



### Optional Enhancements

# 1. *Dynamic Cache Timeout*:
#    - Allow the cache timeout to be configurable via settings or request parameters.

# 2. *Rate Limiting*:
#    - Add rate limiting to prevent excessive API calls to the external endpoint.

# 3. *Parallel Requests*:
#    - Use a library like concurrent.futures to fetch multiple pages in parallel for better performance.

# 4. *Custom Error Responses*:
#    - Return more detailed error messages based on the type of error (e.g., 404, 500).



# This implementation should now handle pagination, caching, and error handling effectively. Let me know if you need further assistance!