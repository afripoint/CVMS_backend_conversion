from accounts.models import CustomUser
from rest_framework import serializers
from django.core.exceptions import ValidationError
import re
import uuid
from django.utils import timezone


# Reusable Password Validator
def validate_password_strength(value):
    """Check if the password meets security criteria."""
    if not re.search(r"[A-Z]", value):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r"[0-9]", value):
        raise ValidationError("Password must contain at least one digit.")
    if not re.search(r"[!@#$%^&*()\-_=+{};:,<.>]", value):
        raise ValidationError("Password must contain at least one special character.")
    return value


# individual register
class IndividualRegistrationSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    other_name = serializers.CharField(max_length=50, required=False)
    phone_number = serializers.CharField(max_length=50)
    address = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    role = serializers.CharField()
    password = serializers.CharField(
        write_only=True, validators=[validate_password_strength]
    )
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = (
            "first_name",
            "last_name",
            "other_name",
            "phone_number",
            "address",
            "role",
            "email",
            "password",
            "confirm_password",
        )

        def validate(self, attrs):
            """Ensure password and confirm_password match."""
            if attrs["password"] != attrs.pop("confirm_password"):
                raise serializers.ValidationError(
                    {"confirm_password": "Passwords must match."}
                )
            return attrs

        def create(self, validated_data):
            validated_data.pop("confirm_password")
            verification_token = str(uuid.uuid4())
            user = CustomUser.objects.create_user(
                email=validated_data["email"],
                password=validated_data["password"],
                role=validated_data["role"],
                token=verification_token,
                otp_created_at=timezone.now(),
            )
            return user


# Agent Registration Serializer
class AgentCompanyRegistrationSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    other_name = serializers.CharField(max_length=50, required=False)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=50)
    address = serializers.CharField(max_length=100)
    agency_name = serializers.CharField(max_length=255)
    role = serializers.CharField()
    declarant_code = serializers.CharField(max_length=100)
    is_accredify = serializers.BooleanField()
    cac = serializers.CharField(write_only=True)
    password = serializers.CharField(
        write_only=True, validators=[validate_password_strength]
    )
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = (
            "first_name",
            "last_name",
            "other_name",
            "email",
            "phone_number",
            "address",
            "agency_name",
            "role",
            "declarant_code",
            "is_accredify",
            "cac",
            "password",
            "confirm_password",
        )

    def validate(self, data):
        """Ensure password and confirm_password match."""
        if data["password"] != data.pop("confirm_password"):
            raise serializers.ValidationError(
                {"confirm_password": "Passwords must match."}
            )
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        verification_token = str(uuid.uuid4())
        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            role=validated_data["role"],
            token=verification_token,
            otp_created_at=timezone.now(),
        )

        return user


# # Company Registration Serializer
# class CompanyRegistrationSerializer(serializers.ModelSerializer):
#     first_name = serializers.CharField(max_length=50)
#     last_name = serializers.CharField(max_length=50)
#     other_name = serializers.CharField(max_length=50, required=False)
#     email = serializers.EmailField()
#     phone_number = serializers.CharField(max_length=50)
#     address = serializers.CharField(max_length=100)
#     agency_name = serializers.CharField(max_length=255)
#     role = serializers.CharField()
#     declarant_code = serializers.CharField(max_length=100)
#     is_accredify = serializers.BooleanField()
#     cac = serializers.CharField(write_only=True)
#     password = serializers.CharField(
#         write_only=True, validators=[validate_password_strength]
#     )
#     confirm_password = serializers.CharField(write_only=True)

#     class Meta:
#         model = CustomUser
#         fields = (
#             "first_name",
#             "last_name",
#             "other_name",
#             "email",
#             "phone_number",
#             "address",
#             "agency_name",
#             "role",
#             "declarant_code",
#             "is_accredify",
#             "cac",
#             "password",
#             "confirm_password",
#         )

#     def validate(self, data):
#         """Ensure password and confirm_password match."""
#         if data["password"] != data.pop("confirm_password"):
#             raise serializers.ValidationError(
#                 {"confirm_password": "Passwords must match."}
#             )
#         return data

#     def create(self, validated_data):
#         validated_data.pop("confirm_password")
#         user = CustomUser.objects.create_user(
#             email=validated_data["email"],
#             password=validated_data["password"],
#             role=validated_data["role"],
#         )

#         return user


class NINVerificationSerializer(serializers.Serializer):
    nin = serializers.CharField(max_length=11, min_length=11, required=True)


class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, data):
        """Ensure email is provided"""
        if not data["email"]:
            raise serializers.ValidationError({"Email": "Email is required."})
        return data


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        # Ensure both email and password are provided
        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")
        
        # Verify user exists and is verified
        try:
            user = CustomUser.objects.get(email=email)
            if not user.is_verified and not user.is_active:
                # the frontend developer should redirect to the resend OTP screen
                raise serializers.ValidationError("Inactive user - activate your account")
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        return data
