# from api_keys.models import APIKey
# from rest_framework.authentication import BaseAuthentication
# from rest_framework.exceptions import AuthenticationFailed
# from django.conf import settings


# class APIKeyAuthentication(BaseAuthentication):
#     def authenticate(self, request):
#         x_api_key = request.headers.get("X-API-Key")
#         if not x_api_key:
#             raise AuthenticationFailed("API key required")

#         try:
#             api_key = APIKey.objects.get(key=x_api_key, is_active=True)
#         except APIKey.DoesNotExist:
#             raise AuthenticationFailed("Invalid API Key")

#         return (api_key, None)  
