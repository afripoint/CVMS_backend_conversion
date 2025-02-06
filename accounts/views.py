from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import uuid
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from accounts.models import CompanyProfile, CustomUser, SubAccount
from django.utils import timezone
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from datetime import timedelta
from accounts.serializers import (
    AgentRegistrationSerializer,
    CompanyRegistrationSerializer,
    IndividualRegistrationSerializer,
    LoginSerializer,
    NINVerificationSerializer,
    ResendOTPSerializer,
    SubAccountDetailSerializer,
    SubAccountSerializer,
)
from accounts.tokens import create_jwt_pair_for_user
from accounts.utils import generateRandomOTP, verify_nin
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
        elif role == "agent account/freight forwarders":
            return AgentRegistrationSerializer

        elif role == "company account":
            return CompanyRegistrationSerializer
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

        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            verification_token = str(uuid.uuid4())
            generated_otp = generateRandomOTP(100000, 999999)
            email = serializer.validated_data["email"]
            user = serializer.save()
            user.otp = str(generated_otp)
            user.token = verification_token
            user.save()

            url = request.build_absolute_uri(
                f"auth/verify-otp/?token={verification_token}"
            )
            subject = "Verify your account"

            email_html_message = render_to_string(
                "accounts/verification_email.html",
                {
                    "otp": generated_otp,
                    "verification_link": url,
                },
            )
            email_plain_message = strip_tags(email_html_message)
            send_mail(
                subject=subject,
                message=email_plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=email_html_message,
            )

            return Response(
                {"message": "OTP has been sent to your email"},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Verify OTP
class VerifyOTPAPIView(APIView):
    @swagger_auto_schema(
        operation_summary="Verify OTP",
        operation_description="This endpoint verifies an OTP sent to the user's email. "
        "It checks if the OTP is valid, not expired, and has not been used before. "
        "Once verified, the user account is activated.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "otp": openapi.Schema(
                    type=openapi.TYPE_STRING, description="The OTP sent to the user"
                ),
            },
            required=["otp"],
        ),
        manual_parameters=[
            openapi.Parameter(
                "token",
                openapi.IN_QUERY,
                description="Unique verification token associated with the user",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={
            200: openapi.Response(
                description="Email verified successfully",
                examples={
                    "application/json": {"message": "Email verified successfully"}
                },
            ),
            400: openapi.Response(
                description="Invalid request",
                examples={
                    "application/json": {"error": "OTP and token are required"},
                },
            ),
        },
    )
    def post(self, request):
        otp = request.data.get("otp", "")
        token = request.query_params.get("token")

        if not otp or not token:
            return Response(
                {"error": "OTP and token are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = CustomUser.objects.get(token=token, otp=otp)
        except CustomUser.DoesNotExist:
            return Response({"error": "Invalid OTP or Token"})

        if user.otp_created_at and (
            timezone.now() - user.otp_created_at > timedelta(minutes=10)
        ):
            return Response(
                {"error": "OTP has expired"}, status=status.HTTP_400_BAD_REQUEST
            )

        if user.otp_used:
            return Response(
                {"error": "OTP has been used"}, status=status.HTTP_400_BAD_REQUEST
            )

        # mark the user as verified
        user.is_verified = True
        user.is_active = True
        user.otp = None
        user.token = None
        user.otp_created_at = None
        user.otp_used = True

        user.save()

        url = request.build_absolute_uri(f"auth/verify-cac/")
        subject = "Account Created - Verification Pending"

        email_html_message = render_to_string(
            "accounts/verification_cac.html",
            {
                "verification_link": url,
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
            {"message": "Email verified successfully"}, status=status.HTTP_200_OK
        )


# Resend OTP
class ResendOTPView(APIView):
    @swagger_auto_schema(
        operation_summary="Resend OTP",
        operation_description="This endpoint allows users to request a new OTP if their OTP expired.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    description="Email associated with the user account",
                ),
            },
            required=["email"],
        ),
        responses={
            201: openapi.Response(
                description="OTP resent successfully",
                examples={
                    "application/json": {"message": "OTP has been sent to your email"}
                },
            ),
            400: openapi.Response(
                description="Invalid request",
                examples={"application/json": {"error": "Invalid data"}},
            ),
            404: openapi.Response(
                description="User not found",
                examples={
                    "application/json": {"error": "User with this email not found"}
                },
            ),
        },
    )
    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]

            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                return Response(
                    {"error": "User with this email not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            verification_token = str(uuid.uuid4())
            user.token = verification_token
            generated_otp = generateRandomOTP(100000, 999999)
            user.otp = str(generated_otp)
            user.otp_created_at = timezone.now()

            user.save()

            url = request.build_absolute_uri(f"/verify-otp/?token={verification_token}")
            subject = "Verify your account"

            email_html_message = render_to_string(
                "accounts/verification_email.html",
                {"otp": generated_otp, "verification_link": url},
            )
            email_plain_message = strip_tags(email_html_message)
            send_mail(
                subject=subject,
                message=email_plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=email_html_message,
            )

            return Response(
                {"message": "OTP has been sent to your email"},
                status=status.HTTP_201_CREATED,
            )
        return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)


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
                    "accounts/NIN_verification_email.html",
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


# login
class LoginAPIView(APIView):
    @swagger_auto_schema(
        operation_summary="User Login",
        operation_description="This endpoint allows users to log in using their email and password.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    description="Registered email of the user",
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_PASSWORD,
                    description="User's password",
                ),
            },
            required=["email", "password"],
        ),
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
                        "message": "Login successfully",
                        "tokens": {
                            "access": "your_access_token_here",
                            "refresh": "your_refresh_token_here",
                        },
                    }
                },
            ),
            400: openapi.Response(
                description="Invalid credentials",
                examples={"application/json": {"message": "Invalid credentials"}},
            ),
        },
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract the email and password of the user
        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")

        # Authenticate the user
        authenticated_user = authenticate(
            request=request,
            username=email,
            password=password,
        )

        if authenticated_user is None:
            return Response(
                {"message": "Invalid credentials"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate tokens and return user info
        tokens = create_jwt_pair_for_user(authenticated_user)

        return Response(
            {
                "message": "Login successfully",
                "tokens": tokens,
                "user": {
                    "first_name": authenticated_user.first_name,
                    "last_name": authenticated_user.last_name,
                    "NIN Verified": authenticated_user.is_NIN_verified,
                },
            }
        )


# create sub_account
class CreateSubUserView(APIView):
    """
    API view for creating a sub-user under a company account.
    Only users with the 'company account' role can create sub-users.
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        summary="Create a Sub-User",
        description="This endpoint allows company accounts to create sub-users.",
        request_body=SubAccountSerializer,
        responses={
            201: SubAccountSerializer,
            400: "Validation errors",
            403: "Unauthorized access",
        },
    )
    def post(self, request, *args, **kwargs):
        company_profile = request.user.company

        # Ensure the user is a company account
        if request.user.role != "company account":
            return Response(
                {"message": "Only company accounts can create sub-users."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not company_profile.is_cac_verified:
            return Response(
                {"message": "Only verified CAC account can create sub-accounts"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if company_profile.limit > 5:
            return Response(
                {"message": "You have exceeded your limit of creating a sub_account"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Pass the company profile to the serializer context
        serializer = SubAccountSerializer(
            data=request.data, context={"company": company_profile}
        )

        if serializer.is_valid():
            sub_user = serializer.save()
            company_profile.limit += 1

            company_profile.save()

            response = {
                "message": "Sub-account created successfully.",
                "data": serializer.data,
                "slug": sub_user.slug,
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)


class SubAccountListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    """
    API view for retrieving a list of sub-accounts.
    Only authenticated users can access it.
    """

    def get(self, request):
        # Retrieve the sub-accounts for the user's company
        sub_accounts = SubAccount.objects.filter(company=request.user.company)

        # Serialize the list of sub-accounts
        serializer = SubAccountDetailSerializer(sub_accounts, many=True)

        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)


# Sub Account Details
class SubAccountDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    """
    API view for retrieving details of a specific sub-account.
    Only authenticated users can access it.
    """

    def get(self, request, slug):
        sub_account = get_object_or_404(
            SubAccount, slug=slug, company=request.user.company
        )
        serializer = SubAccountDetailSerializer(sub_account)

        return Response(serializer.data, status=status.HTTP_200_OK)


# Deactivate a subaccount
class DeactivateActivateSubAccountAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        operation_description="Deactivate and activate a sub-account by slug",
        responses={
            200: "Sub-account deactivated/activated successfully.",
            404: "Sub-account not found.",
        },
    )
    def patch(self, request, slug):
        try:
            sub_account = SubAccount.objects.get(
                slug=slug, company=request.user.company
            )

            # Toggle the 'is_active' and 'is_verified' status
            user = sub_account.user
            if user.is_active:
                user.is_active = False
                user.is_verified = False
                message = "Sub-account has been deactivated successfully."
            else:
                user.is_active = True
                user.is_verified = True
                message = "Sub-account has been activated successfully."

            user.save()

            return Response(
                {"message": message},
                status=status.HTTP_200_OK,
            )

        except SubAccount.DoesNotExist:
            return Response(
                {"error": "Sub-account not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
