from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from smtplib import SMTPException
from django.core.exceptions import ObjectDoesNotExist
import uuid
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from accounts.models import (
    AuthLog,
    CustomUser,
    PasswordResetToken,
    SubAccount,
)
from rest_framework import generics, permissions
from django.utils.encoding import DjangoUnicodeDecodeError
from django.utils import timezone
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from datetime import timedelta
from accounts.serializers import (
    AgentRegistrationSerializer,
    AuthLogSerializer,
    CompanyRegistrationSerializer,
    ForgetPasswordEmailRequestSerializer,
    IndividualRegistrationSerializer,
    LoginSerializer,
    ResendOTPSerializer,
    SetNewPasswordSerializer,
    SubAccountDetailSerializer,
    SubAccountSerializer,
)
from accounts.tokens import create_jwt_pair_for_user
from accounts.utils import (
    TokenGenerator,
    generateRandomOTP,
    get_client_ip,
    get_user_agent,
)
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.send_otp_sms import send_otp_message


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
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)

        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            # Extract the email and password of the user
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            if user.login_attempt > 3:
                if not user.reset_link_sent:
                    token = str(uuid.uuid4())
                    user.reset_link_token = token
                    user.reset_link_sent = True
                    user.is_active = False
                    user.save()

                    reset_url = request.build_absolute_uri(
                        f"auth/reset-password/?token={token}"
                    )

                    subject = "Reset Password Link"

                    email_html_message = render_to_string(
                        "accounts/reset_password_email.html",
                        {
                            "reset_url": reset_url,
                            "first_name": user.first_name.title(),
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
                    {
                        "message": "Your account is locked. check your email for a reset link"
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Authenticate the user
            authenticated_user = authenticate(
                request=request, username=email, password=password
            )

            if authenticated_user is None:
                user.login_attempt += 1
                user.save()

                # failure log
                AuthLog.objects.create(
                    user=user,
                    event_type="Login Failed",
                    ip_address=ip_address,
                    user_agent=user_agent,
                    failure_reason="Invalid credentials - password",
                )
                return Response(
                    {"message": "Invalid credentials"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            tokens = create_jwt_pair_for_user(authenticated_user)
            user.login_attempt = 0
            user.save()
            # success logs
            AuthLog.objects.create(
                user=user,
                event_type="Login Success",
                ip_address=ip_address,
                user_agent=user_agent,
            )
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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# create sub_account
class CreateSubUserView(APIView):
    """
    API view for creating a sub-user under a company or agent account.
    Only users with the 'company account' or 'agent account/freight forwarders' role can create sub-users.
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
        user = request.user
        # company_profile = request.user.company

        # Ensure the user is either a company or an agent
        if user.role not in ["company account", "agent account/freight forwarders"]:
            return Response(
                {"message": "Only company or agent accounts can create sub-users."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Determine whether it's a company or agent creating the sub-user
        profile = None

        if user.role == "company account":
            profile = user.company
        elif user.role == "agent account/freight forwarders":
            profile = user.agent

        if not profile or not profile.is_cac_verified:
            return Response(
                {"message": "Only verified CAC accounts can create sub-accounts."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check the creation limit
        if profile.limit >= 5:
            return Response(
                {"message": "You have exceeded your limit of creating a sub_account."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Pass the profile (company or agent) to the serializer context
        # Pass the profile (company or agent) to the serializer context
        serializer = SubAccountSerializer(
            data=request.data, context={"profile": profile}
        )
        if serializer.is_valid():
            sub_user = serializer.save()

            # Increment the sub-account limit
            profile.limit += 1
            profile.save()

            response = {
                "message": "Sub-account created successfully.",
                "data": serializer.data,
                "slug": sub_user.slug,
            }
            return Response(response, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubAccountListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    """
    API view for retrieving a list of sub-accounts.
    Only authenticated users can access it.
    """

    def get(self, request):
        user = request.user

        # Retrieve the sub-accounts for the user's company
        if user.role == "company account":
            sub_accounts = SubAccount.objects.filter(company=request.user.company)
        elif user.role == "agent account/freight forwarders":
            sub_accounts = SubAccount.objects.filter(agent=request.user.agent)

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
        user = request.user

        # Retrieve the sub-accounts for the user's company/agent
        if user.role == "company account":
            sub_account = get_object_or_404(
                SubAccount, slug=slug, company=request.user.company
            )
        elif user.role == "agent account/freight forwarders":
            sub_account = get_object_or_404(
                SubAccount, slug=slug, agent=request.user.agent
            )

        serializer = SubAccountDetailSerializer(sub_account)

        return Response(serializer.data, status=status.HTTP_200_OK)


# Deactivate a SubAccount
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
        user = request.user
        try:
            # Retrieve the sub-accounts for the user's company/agent
            if user.role == "company account":
                sub_account = SubAccount.objects.get(
                    slug=slug, company=request.user.company
                )
            elif user.role == "agent account/freight forwarders":
                sub_account = SubAccount.objects.get(
                    slug=slug, agent=request.user.agent
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


# forget Password
class ForgetPasswordAPIView(APIView):
    @swagger_auto_schema(
        operation_summary="Request Password Reset",
        operation_description="""
        This endpoint is responsible for initiating the password reset process by collecting the user's email address.

        ### Workflow:
        1. **Email Validation:** The system verifies if the email belongs to a registered user.
        2. **Token Generation:** If the email is valid, a unique password reset token is generated.
        3. **Email Dispatch:** A password reset link containing the token is sent to the user's email.
        4. **Error Handling:** Errors related to email delivery (SMTP, connection, timeout) are handled gracefully.

        ### Request Fields:
        - **email_address** (string): The registered email address of the user requesting a password reset.

        ### Responses:
        - **200 OK**: Password reset email sent successfully.
        - **404 Not Found**: User with the provided email does not exist.
        - **500 Internal Server Error**: An error occurred while sending the reset email (SMTP issues, connection refused, or timeout).
        - **400 Bad Request**: Invalid input data.

        ### Example Usage:
        ```
        POST /api/forgot-password/
        {
            "email_address": "user@example.com"
        }
        ```

        ### Example Response (Success):
        ```
        HTTP 200 OK
        {
            "message": "Reset email successfully sent. Please check your email.",
            "uidb64": "encoded_user_id",
            "token": "generated_token"
        }
        ```

        ### Example Response (User Not Found):
        ```
        HTTP 404 Not Found
        {
            "message": "User with this email does not exist."
        }
        ```

        ### Example Response (SMTP Error):
        ```
        HTTP 500 Internal Server Error
        {
            "message": "There was an error sending the reset email. Please try again later.",
            "error": "SMTPException details"
        }
        ```

        ### Example Response (Connection Error):
        ```
        HTTP 500 Internal Server Error
        {
            "message": "Could not connect to the email server. Please check your email settings.",
            "error": "ConnectionRefusedError details"
        }
        ```

        ### Example Response (Timeout):
        ```
        HTTP 500 Internal Server Error
        {
            "message": "Email server timeout. Please try again later.",
            "error": "TimeoutError details"
        }
        ```
        """,
        request_body=ForgetPasswordEmailRequestSerializer,
    )
    def post(self, request):
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        serializer = ForgetPasswordEmailRequestSerializer(data=request.data)
        if serializer.is_valid():
            email_address = serializer.validated_data["email_address"]
            try:
                user = CustomUser.objects.get(email_address=email_address)
            except ObjectDoesNotExist:
                response = {
                    "message": "User with this email does not exist.",
                }
                return Response(data=response, status=status.HTTP_404_NOT_FOUND)

            # Generate activation token
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            generate_token = TokenGenerator()
            token = generate_token.make_token(user)
            expired_at = timezone.now() + timezone.timedelta(hours=1)
            first_name = user.first_name

            # create the token
            PasswordResetToken.objects.create(
                user=user,
                token=token,
                expired_at=expired_at,
            )

            # Construct activation link
            activation_link = request.build_absolute_uri(
                reverse(
                    "reset-password-token-check",
                    kwargs={"uidb64": uid, "token": token},
                )
            )
            # Send reset password email
            subject = "Reset Your Password"

            email_html_message = render_to_string(
                "accounts/reset_password_email.html",
                {
                    "first_name": first_name,
                    "activation_link": activation_link,
                },
            )
            email_plain_message = strip_tags(email_html_message)

            try:

                send_mail(
                    subject=subject,
                    message=email_plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email_address],
                    html_message=email_html_message,
                )

                # password reset log
                AuthLog.objects.create(
                    user=user,
                    event_type="Password Reset Request",
                    ip_address=ip_address,
                    user_agent=user_agent,
                )

                response = {
                    "message": "Reset email successfully sent. Please check your email.",
                    "uidb64": uid,
                    "token": token,
                }
                return Response(data=response, status=status.HTTP_200_OK)

            except SMTPException as e:
                response = {
                    "message": "There was an error sending the reset email. Please try again later.",
                    "error": str(e),
                }
                return Response(
                    data=response, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            except ConnectionRefusedError as e:
                response = {
                    "message": "Could not connect to the email server. Please check your email settings.",
                    "error": str(e),
                }
                return Response(
                    data=response, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            except TimeoutError as e:
                response = {
                    "message": "Email server timeout. Please try again later.",
                    "error": str(e),
                }
                return Response(
                    data=response, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# password token check
class PasswordTokenCheck(APIView):
    def get(self, request, uidb64, token):

        try:
            uid = urlsafe_base64_decode(uidb64).decode()

            user = CustomUser.objects.get(pk=uid)

            # check if the token has been used
            # token_generator = PasswordResetTokenGenerator()

            token_generator = TokenGenerator()

            if not token_generator.check_token(user, token):
                # Redirect to the frontend URL with an invalid token status
                return Response(
                    {"error": "Token has been used"}, status=status.HTTP_400_BAD_REQUEST
                )
                # return HttpResponseRedirect(
                #     # "https://cvms-admin.vercel.app/#/auth/reset-password?status=invalid",
                #     # status=400,
                # )

            if user.expired_at < timezone.now():
                response = {"message": "Token has expired, please generate another one"}
                return (Response(data=response, status=status.HTTP_404_NOT_FOUND),)

            # return Response(
            #     {
            #         "message": True,
            #         "messge": "Credentials valid",
            #         "uidb64": uidb64,
            #         "token": token,
            #     },
            #     status=status.HTTP_200_OK,
            # )

            # return HttpResponse(
            #     "Token Valid and successful, redirecting to the change password page"
            # )
            return HttpResponseRedirect(
                f"https://cvms-portal.vercel.app/#/auth/reset-password?uidb64={uidb64}&token={token}&status=valid"
            )

        # except DjangoUnicodeDecodeError as e:
        #     return Response({"error": "Tokeen is not valid, please request a new one"})
        except DjangoUnicodeDecodeError as e:
            # Redirect to the frontend URL with an invalid token status
            # return HttpResponse(
            #     "Token invalid, please cheeck tokeen; redirect to login screen"
            # )
            return HttpResponseRedirect(
                "https://cvms-portal.vercel.app/#/auth/reset-password?status=invalid",
                status=400,
            )


class SetNewPasswordAPIView(APIView):
    @swagger_auto_schema(
        operation_summary="Reset User's Password",
        operation_description="""
        This endpoint allows the user to reset their password after verifying their token and UID. The new password must meet the following security criteria:

        ### Password Requirements:
        - **At least one uppercase letter** (A-Z)
        - **At least one digit** (0-9)
        - **At least one special character** from the set: `!@#$%^&*()-_=+{};:,<.>`

        ### Workflow:
        1. **Token and UID Validation:** The system validates the provided user ID (UID) and password reset token.
        2. **Password Update:** If the token is valid and has not expired, the user's password is updated with the new password.
        3. **Token Invalidation:** The token is marked as used, and further requests with this token will be rejected.

        ### Common Error Responses:
        - **400 Bad Request**: Invalid or missing token, invalid UID, or non-compliant password.
        - **400 Token Expired**: Token has expired and can no longer be used.
        - **400 Token Already Used**: Token has already been used to reset the password.
        - **200 OK**: Password reset was successful.

        ### Example Usage:
        ```
        PATCH /api/set-new-password/
        {
            "uidb64": "encoded_user_id",
            "token": "reset_token",
            "password": "NewPassword123!"
        }
        ```

        ### Example Responses:
        - **Success (200 OK)**:
        ```
        {
            "message": "Password updated successfully."
        }
        ```

        - **Invalid Token (400 Bad Request)**:
        ```
        {
            "error": "Invalid token."
        }
        ```

        - **Token Expired (400 Bad Request)**:
        ```
        {
            "error": "Token has expired."
        }
        ```

        - **Token Already Used (400 Bad Request)**:
        ```
        {
            "error": "Token has already been used."
        }
        ```

        - **Invalid UID (400 Bad Request)**:
        ```
        {
            "error": "Invalid UID or user not found."
        }
        ```

        - **Password Validation Failure (400 Bad Request)**:
        ```
        {
            "password": ["Password must contain at least one uppercase letter, one digit, and one special character."]
        }
        ```
        """,
        request_body=SetNewPasswordSerializer,
    )
    def patch(self, request):
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        serializer = SetNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            password = serializer.validated_data["password"]
            token = serializer.validated_data["token"]
            uidb64 = serializer.validated_data["uidb64"]

            try:
                uid = urlsafe_base64_decode(uidb64).decode()
                user = CustomUser.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
                return Response(
                    {"error": "Invalid UID or user not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                reset_token = PasswordResetToken.objects.get(user=user, token=token)
                if reset_token.is_expired():
                    return Response(
                        {"error": "Token has expired."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if reset_token.used:
                    return Response(
                        {"error": "Token has already been used."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Validate token
                token_generator = TokenGenerator()
                if not token_generator.check_token(user, token):
                    return Response(
                        {"error": "Invalid token for this user."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Set new password and mark token as used
                user.set_password(password)
                user.login_attempts = 0
                user.reset_link_token = None
                user.reset_link_sent = False
                user.is_active = True
                user.save()
                reset_token.used = True
                reset_token.save()

                AuthLog.objects.create(
                    user=user,
                    event_type="Password Reset Completed",
                    ip_address=ip_address,
                    user_agent=user_agent,
                )

                return Response(
                    {"message": "Password updated successfully."},
                    status=status.HTTP_200_OK,
                )

            except PasswordResetToken.DoesNotExist:
                return Response(
                    {"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthLogListView(generics.ListAPIView):
    queryset = AuthLog.objects.all().order_by("-timestamp")
    serializer_class = AuthLogSerializer
    # permission_classes = [permissions.IsAdminUser]
    pagination_class = PageNumberPagination
