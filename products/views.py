from django.shortcuts import render
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework import serializers
from django.urls import reverse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Plan, Product
from .serializers import ProductSerializers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import ProductSerializers


class ProductAPIView(APIView):
    @swagger_auto_schema(
        operation_summary="List all active products",
        operation_description="Retrieve a list of all products that are currently active.",
        responses={200: ProductSerializers(many=True)},
    )
    def get(self, request, *args, **kwargs):
        products = Product.objects.filter(is_active=True)
        serializer = ProductSerializers(products, many=True)
        response = {
            "products": serializer.data,
        }
        return Response(response, status=status.HTTP_200_OK)


class PlanAPIView(APIView):
    @swagger_auto_schema(
        operation_summary="List all plans",
        operation_description="Retrieve a list of all plans that are currently active.",
        responses={200: ProductSerializers(many=True)},
    )
    def get(self, request, *args, **kwargs):
        plans = Plan.objects.filter(is_active=True)
        serializer = ProductSerializers(plans, many=True)
        response = {
            "plans": serializer.data,
        }
        return Response(response, status=status.HTTP_200_OK)
