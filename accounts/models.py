from django.db import models
from typing import Iterable
import secrets
import string
from django.conf import settings
from django.utils.text import slugify
from datetime import timedelta
from django.utils import timezone
import uuid
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

from departments.models import Department

# =================================================================
#                           USER MANAGER MODEL
# =================================================================
class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given phone_number, password, and any extra fields.
        """

        if not email:
            raise ValueError("The Email address is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Creates and saves a superuser with the given phone_number, password, and any extra fields.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if extra_fields.get("is_active") is not True:
            raise ValueError("Superuser must have is_active=True.")
        if extra_fields.get("is_verified") is not True:
            raise ValueError("Superuser must have is_verified=True.")

        return self.create_user(email, password, **extra_fields)


# =================================================================
#                           CUSTOM USER MODEL
# =================================================================
class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_TYPES = (
        ("individual account", "Individual Account"),
        ("agent account/freight forwarders", "Agent Account/Freight forwarders"),
        ("company account", "Company Account"),
    )
    MESSAGE_CHOICES = (
        ("sms", "Sms"),
        ("email", "Email"),
        ("whatsapp", "Whatsapp"),
    )
    email = models.EmailField(max_length=254, unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    other_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255)
    is_accredify = models.BooleanField(default=False)
    # default_password = models.CharField(max_length=50, blank=True, null=True)
    role = models.CharField(
        max_length=100, choices=ROLE_TYPES, default="individual account"
    )
    message_choice = models.CharField(
        max_length=50, choices=MESSAGE_CHOICES, default="sms"
    )
    is_NIN_verified = models.BooleanField(default=False)
    slug = models.CharField(max_length=400, unique=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    token = models.CharField(max_length=150, null=True, blank=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    otp_used = models.BooleanField(default=False)
    otp_pin_id = models.CharField(max_length=150, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    login_attempt = models.IntegerField(default=0)
    reset_link_token = models.CharField(max_length=255, null=True, blank=True)
    reset_link_sent = models.BooleanField(default=False)
    is_sub_account = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"

    objects = UserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["-email"]

    # Checking if the user has a specific permission
    # def has_permission(self, permission_code):
    #     """
    #     Check if the user has a specific permission based on their assigned role.
    #     """
    #     # if self.role:
    #     #     # Check if the role has the specific permission
    #     #     return self.role.permissions.filter(
    #     #         permission_code=permission_code
    #     #     ).exists()
    #     if self.role:
    #          # Get all assigned permission codes to the user's role
    #         role_permissions = self.role.permissions.values_list('permission_code', flat=True)

    #         # Check if the required permission exists in the assigned permissions
    #         return permission_code in role_permissions
    #     return False

    # Generate a secure random password
    @staticmethod
    def generate_default_password(length=12):
        # Generate a secure random password
        characters = string.ascii_letters + string.digits + string.punctuation
        return "".join(secrets.choice(characters) for _ in range(length))
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.phone_number) + str(uuid.uuid4())

        # Generate a default password if not already set
        # if not self.default_password:
        #     self.default_password = self.generate_default_password()

        super().save(*args, **kwargs)


# Password reset token model
class PasswordResetToken(models.Model):
    user = models.ForeignKey(
        CustomUser, related_name="reset_token", on_delete=models.CASCADE
    )
    token = models.CharField(max_length=555, unique=True, blank=True, null=True)
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()

    def is_expired(self):
        return self.expired_at < timezone.now()


# =================================================================
#                           INDIVIDUAL PROFILE MODEL
# =================================================================

class IndividualProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, related_name="individual", on_delete=models.CASCADE
    )
    profile_image = models.ImageField(
        upload_to="profile_images", default="avartar.png", null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.first_name} profile"

    class Meta:
        verbose_name = "individual profile"
        verbose_name_plural = "individual profiles"
        ordering = ["-created_at"]

# =================================================================
#                           AGENT PROFILE MODEL
# =================================================================

class AgentProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, related_name="agent", on_delete=models.CASCADE
    )
    profile_image = models.ImageField(
        upload_to="profile_images", default="avartar.png", null=True, blank=True
    )
    cac = models.CharField(max_length=50, null=True, blank=True)
    cac_certificate = models.ImageField(
        upload_to="cac_certificates", default="avartar.png", null=True, blank=True

    )
    agency_name = models.CharField(max_length=255, null=True, blank=True)
    declarant_code = models.CharField(max_length=255, null=True, blank=True)
    is_cac_verified = models.BooleanField(default=False)
    limit = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.first_name} profile"

    class Meta:
        verbose_name = "agent profile"
        verbose_name_plural = "agent profiles"
        ordering = ["-created_at"]


# =================================================================
#                           COMPANY PROFILE MODEL
# =================================================================

class CompanyProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, related_name="company", on_delete=models.CASCADE
    )
    profile_image = models.ImageField(
        upload_to="profile_images", default="avartar.png", null=True, blank=True
    )
    company_name = models.CharField(max_length=50, null=True, blank=True)
    cac = models.CharField(max_length=50, null=True, blank=True)
    is_cac_verified = models.BooleanField(default=False)
    limit = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.first_name} profile"

    class Meta:
        verbose_name = "company profile"
        verbose_name_plural = "company profiles"
        ordering = ["-created_at"]



# =================================================================
#                           SUB-ACCOUNT MODEL
# =================================================================
class SubAccount(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ("sub-account company", "Sub-Account Company"),
        ("sub-account agent", "Sub-Account Agent"),
    ]
    user = models.OneToOneField(
        CustomUser, related_name="sub_user", on_delete=models.CASCADE
    )
    company = models.ForeignKey(
        CompanyProfile, on_delete=models.CASCADE, related_name="sub_users", null=True, blank=True
    )
    agent = models.ForeignKey(
        AgentProfile, on_delete=models.CASCADE, related_name="sub_users", null=True, blank=True
    )
    slug = models.CharField(max_length=250, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    account_type = models.CharField(max_length=50, choices=ACCOUNT_TYPE_CHOICES)
    phone_number = models.CharField(max_length=15, unique=True)
    location = models.CharField(max_length=255)
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        company_name = self.company.company_name if hasattr(self.company, "company_name") else self.agent.agency_name
        return f"{self.first_name} {self.last_name} - {self.department}"
    class Meta:
        verbose_name = "sub-user"
        verbose_name_plural = "sub-users"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.phone_number) + str(uuid.uuid4())

        super().save(*args, **kwargs)


# =================================================================
#                           AUTHENTICATION LOGS
# =================================================================

class AuthLog(models.Model):
    EVENT_TYPES = [
        ("LOGIN_SUCCESS", "Login Success"),
        ("LOGIN_FAILED", "Login Failed"),
        ("LOGOUT", "Logout"),
        ("PASSWORD_RESET_REQUEST", "Password Reset Request"),
        ("PASSWORD_RESET_COMPLETED", "Password Reset Completed"),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    failure_reason = models.TextField(null=True, blank=True)  # For failed logins

    def __str__(self):
        return f"{self.event_type} - {self.user} - {self.timestamp}"
