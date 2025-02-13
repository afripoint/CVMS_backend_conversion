from accounts.models import (
    AgentProfile,
    AuthLog,
    CompanyProfile,
    CustomUser,
    IndividualProfile,
    SubAccount,
)
from departments.models import Department
from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
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
            raise serializers.ValidationError({"error": "Passwords must match."})
        return attrs

    def create(self, validated_data):

        validated_data.pop("confirm_password", None)

        if CustomUser.objects.filter(email=validated_data["email"]).exists():
            raise serializers.ValidationError(
                {"error": ["A user with this email already exists."]}
            )

        if CustomUser.objects.filter(
            phone_number=validated_data["phone_number"]
        ).exists():
            raise serializers.ValidationError(
                {"error": ["A user with this phone number already exists."]}
            )

        try:
            user = CustomUser.objects.create_user(
                **validated_data,
                otp_created_at=timezone.now(),
            )

            IndividualProfile.objects.create(user=user)

            return user
        except IntegrityError:
            raise serializers.ValidationError(
                {"error": ["An unexpected error occurred. Please try again."]}
            )


# Agent Registration Serializer
class AgentRegistrationSerializer(serializers.ModelSerializer):
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
        """Create an agent user and pass profile data to the signal."""

        agency_name = validated_data.pop("agency_name")
        declarant_code = validated_data.pop("declarant_code")
        cac = validated_data.pop("cac")

        validated_data.pop("confirm_password", None)

        if CustomUser.objects.filter(email=validated_data["email"]).exists():
            raise serializers.ValidationError(
                {"email": ["A user with this email already exists."]}
            )

        if CustomUser.objects.filter(
            phone_number=validated_data["phone_number"]
        ).exists():
            raise serializers.ValidationError(
                {"phone_number": ["A user with this phone number already exists."]}
            )
        try:
            user = CustomUser.objects.create_user(
                otp_created_at=timezone.now(),
                **validated_data,
            )

            AgentProfile.objects.create(
                user=user,
                agency_name=agency_name,
                cac=cac,
                declarant_code=declarant_code,
            )
            return user

        except IntegrityError:
            raise serializers.ValidationError(
                {"error": ["An unexpected error occurred. Please try again."]}
            )


# Company Registration Serializer
class CompanyRegistrationSerializer(serializers.ModelSerializer):
    role = serializers.CharField()
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    other_name = serializers.CharField(max_length=50, required=False)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=50)
    address = serializers.CharField(max_length=100)
    company_name = serializers.CharField(max_length=255)
    cac = serializers.CharField(write_only=True)
    is_accredify = serializers.BooleanField()
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
            "company_name",
            "role",
            "cac",
            "is_accredify",
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
        validated_data.pop("confirm_password", None)

        company_name = validated_data.pop("company_name")
        cac = validated_data.pop("cac")

        # Check for existing email and phone_number before attempting to create the user
        if CustomUser.objects.filter(email=validated_data["email"]).exists():
            raise serializers.ValidationError(
                {"email": ["A user with this email already exists."]}
            )

        if CustomUser.objects.filter(
            phone_number=validated_data["phone_number"]
        ).exists():
            raise serializers.ValidationError(
                {"phone_number": ["A user with this phone number already exists."]}
            )

        try:
            user = CustomUser.objects.create_user(
                **validated_data,
                otp_created_at=timezone.now(),
            )

            # Create CompanyProfile directly
            CompanyProfile.objects.create(user=user, company_name=company_name, cac=cac)

            return user

        except IntegrityError:
            raise serializers.ValidationError(
                {"error": ["An unexpected error occurred. Please try again."]}
            )


# RESEND OTP SERIALIZER
class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, data):
        """Ensure email is provided"""
        if not data["email"]:
            raise serializers.ValidationError({"Email": "Email is required."})
        return data


# LOGIN SERIALIZER
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
                raise serializers.ValidationError(
                    "Inactive user - activate your account"
                )
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        return data


# SUB ACCOUNT SERIALIZER
class SubAccountSerializer(serializers.ModelSerializer):
    department = serializers.SlugRelatedField(
        queryset=Department.objects.all(), slug_field="department", required=True
    )
    password = serializers.CharField(
        write_only=True, validators=[validate_password_strength]
    )
    account_type = serializers.ChoiceField(
        choices=SubAccount.ACCOUNT_TYPE_CHOICES, required=True
    )
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = SubAccount
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "location",
            "account_type",
            "department",
            "password",
            "confirm_password",
        )

    def validate(self, data):
        # Ensure account_type is provided and valid
        if "account_type" not in data:
            raise serializers.ValidationError(
                {"account_type": "This field is required."}
            )

        # Check if password and confirm_password match
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        # Remove confirm_password from validated data
        validated_data.pop("confirm_password", None)
        # extract the related forien key data
        department = validated_data.pop("department")

        profile = self.context.get("profile")  # Could be CompanyProfile or AgentProfile

        if not profile:
            raise serializers.ValidationError(
                {"profile": "Profile context is required (Company or Agent)."}
            )

        # Create the user with the correct role
        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            password=validated_data.pop("password"),  # Password hashing happens here
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone_number=validated_data["phone_number"],
            role="sub_account",
            is_sub_account=True,
        )

        user.is_active = True
        user.is_verified = True

        user.save()

        # Create sub-account
        sub_account = SubAccount.objects.create(
            user=user,
            company=profile if isinstance(profile, CompanyProfile) else None,
            agent=profile if isinstance(profile, AgentProfile) else None,
            department=department,
            **validated_data,
        )

        sub_account.save

        return sub_account


class SubAccountDetailSerializer(serializers.ModelSerializer):
    department = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()
    agent = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = SubAccount
        fields = "__all__"

    def get_department(self, obj):
        # Since the 'department' is a ForeignKey to a SubAccount model
        return obj.department.department if obj.department else None

    def get_company(self, obj):
        # Since the 'company' is a ForeignKey to a SubAccount model
        return obj.company.company_name if obj.company else None
    
    def get_agent(self, obj):
        # Since the 'agent' is a ForeignKey to a subAccount model
        return obj.agent.agency_name if obj.agent else None

    def get_user(self, obj):
        # Since the want the user's full name
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user else None


# Forgot Password
class ForgetPasswordEmailRequestSerializer(serializers.Serializer):
    email_address = serializers.EmailField(min_length=8)


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=8, write_only=True, required=True)
    confirm_password = serializers.CharField(
        min_length=8, write_only=True, required=True
    )
    token = serializers.CharField(write_only=True, required=True)
    uidb64 = serializers.CharField(write_only=True, required=True)

    def validate_password(self, value):
        if not re.search(r"[A-Z]", value):
            raise ValidationError(
                "Password must contain at least one uppercase letter."
            )
        if not re.search(r"[0-9]", value):
            raise ValidationError("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*()\-_=+{};:,<.>]", value):
            raise ValidationError(
                "Password must contain at least one special character."
            )
        return value

    def validate(self, attrs):
        password = attrs.get("password", "").strip()
        confirm_password = attrs.get("confirm_password", "").strip()

        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")

        # Assuming token and uidb64 validation is handled in the view
        return attrs


class AuthLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthLog
        fields = "__all__"
