from accounts.models import CustomUser
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from verifications.serializers import (
    CACVerificationSerializers,
    NINVerificationSerializer,
)
from verifications.utils import verify_nin
from rest_framework.response import Response
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated


# NIN verification
class NINVerificationAPIView(APIView):
    """
    API endpoint to verify NIN using Dojah
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

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

            try:
                nin_details = verify_nin(nin)
            except Exception as e:
                return Response(
                    {"error": "NIN is invalid - {e}"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # if "error" in nin_details:
            #     return Response(
            #         {"error": "NIN not found, please verify your NIN."},
            #         status=status.HTTP_400_BAD_REQUEST,
            #     )

            # Compare first and last names
            if (
                user.first_name.lower() == nin_details["first_name"].lower()
                and user.last_name.lower() == nin_details["last_name"].lower()
            ):
                user.is_NIN_verified = True
                # send email

                subject = "NIN Verification"

                email_html_message = render_to_string(
                    "verifications/NIN_verification_email.html",
                    {
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "nin": nin,
                    },
                )
                email_plain_message = strip_tags(email_html_message)
                send_mail(
                    subject=subject,
                    message=email_plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=email_html_message,
                )
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


class CACVerificationRequestAPIView(APIView):
    """
    API view for handling CAC verification requests.
    Users must provide valid PNG, JPG, or PDF files (≤ 10MB).
    """

    @swagger_auto_schema(
        operation_summary="Submit CAC Verification Request",
        operation_description="Allows a user to submit CAC verification documents (CAC certificate, status certificate, and letter of authorization).",
        request_body=CACVerificationSerializers,
        responses={
            200: openapi.Response(
                description="Verification request submitted successfully.",
                examples={
                    "application/json": {
                        "message": "Verification request successfully, please check your email"
                    }
                },
            ),
            400: openapi.Response(
                description="Validation errors or user not found.",
                examples={"application/json": {"error": "User does not exist"}},
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        user = request.user

        serializer = CACVerificationSerializers(request.data)
        if serializer.is_valid(user=user):
            serializer.save()
            email = serializer.validated_data["email"]
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                return Response(
                    {"error": "User does not exist"}, status=status.HTTP_400_BAD_REQUEST
                )

            subject = "CAC Verification Request"

            email_html_message = render_to_string(
                "verifications/CAC_verification_email.html",
                {
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
            )
            email_plain_message = strip_tags(email_html_message)
            send_mail(
                subject=subject,
                message=email_plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=email_html_message,
            )
            return Response(
                {
                    "message": "Verification request successfully, please check your email",
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
