# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework.permissions import IsAdminUser
# from .models import APIKey
# from .serializers import APIKeySerializer


# class ListAPIKeysView(APIView):
#     permission_classes = [IsAdminUser]

#     def get(self, request):
#         api_keys = APIKey.objects.filter(user=request.user)
#         serializer = APIKeySerializer(api_keys, many=True)
#         return Response(serializer.data)


# # Generate a New API Key
# class GenerateAPIKeyView(APIView):
#     def post(self, request):
#         api_key = APIKey.objects.create()
#         response = {
#             "message": "API key generated successfully",
#             "message": api_key,
#         }

#         return Response(response, status=201)
    
# # revoke an API key
# class RevokeAPIKeyView(APIView):
#     def post(self, request):
#         key = request.data.get("api_key")
#         try:
#             api_key = APIKey.objects.get(key=key)
#             api_key.is_active = False
#             api_key.save()
#             return Response({"message": "API key revoked successfully"}, status=200)
#         except APIKey.DoesNotExist:
#             return Response({"error": "Invalid API Key"}, status=400)
