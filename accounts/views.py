from django.shortcuts import render
from accounts.serializers import (
    AgentCompanyRegistrationSerializer,
    IndividualRegistrationSerializer,
    NINVerificationSerializer,
)
from accounts.utils import verify_nin
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class RegistrationAPIView(APIView):
    def get_serializer_class(self, role):
        if role == "individual account":
            return IndividualRegistrationSerializer
        elif role in ["agent account/freight forwarders", "company account"]:
            return AgentCompanyRegistrationSerializer
        return None

    @swagger_auto_schema(
        operation_summary="User Registration Endpoint",
        operation_description="This endpoint allows users to register based on their role. Different fields are required for different roles.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "role": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="User role (individual account, agent account/freight forwarders, company account)",
                    enum=[
                        "individual account",
                        "agent account/freight forwarders",
                        "company account",
                    ],
                )
            },
            required=["role"],
        ),
    )
    def post(self, request, *args, **kwargs):
        role = request.data.get("role")
        serializer_class = self.get_serializer_class(role)

        if not serializer_class:
            return Response(
                {"error": "Invalid role type"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Dynamically set request body in Swagger
        self.schema = getattr(serializer_class, "swagger_schema", None)

        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # generate OTP and send OTP to registered user email
            # save OTP to the database
           

            
            return Response(
                {"message": "User registered successfully", "user_id": user.id},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# NIN verification
class NINVerificationAPIView(APIView):
    """
    API endpoint to verify NIN using Dojah
    """

    @swagger_auto_schema(
        operation_summary="Verify NIN endpoint",
        operation_description="Allow users to verify their NIN",
        request_body=NINVerificationSerializer,
        responses={
            201: openapi.Response(
                description="NIN verified successfully",
                examples={
                    "application/json": {"message": "Product added successfully"}
                },
            ),
            400: openapi.Response(
                description="Validation error",
                examples={
                    "application/json": {"error": ["NIN not found for this record."]}
                },
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = NINVerificationSerializer(data=request.data)
        user = request.user
        if serializer.is_valid():
            nin = serializer.validated_data["nin"]
            nin_details = verify_nin(nin)

            if "error" in nin_details:
                return Response(
                    {"error": "NIN not found, please verify your NIN."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Compare first and last names
            if (
                user.first_name.lower() == nin_details["first_name"].lower()
                and user.last_name.lower() == nin_details["last_name"].lower()
            ):
                user.is_NIN_verification = True
                return Response(
                    {
                        "message": "NIN verified successfully",
                        "first_name": nin_details["first_name"],
                        "last_name": nin_details["last_name"],
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(
                {"error": "NIN found but details does not match"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Verify OTP
# display if the user is NIN verified as a response to be used by the frontend developer for prompt notification after setting is_verified = True and is_active = True
# clear the OTP after verify



# Things to work on
# verify OTP
# google smtp
# login
