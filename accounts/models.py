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


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_TYPES = (
        ("individual account", "Individual Account"),
        ("agent account/freight forwarders", "Agent Account/Freight forwarders"),
        ("company account", "Company Account"),
    )
    email = models.EmailField(max_length=254, unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    other_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255)
    agency_name = models.CharField(max_length=255)
    declarant_code = models.CharField(max_length=255)
    cac = models.CharField(max_length=50)
    is_accredify = models.BooleanField(default=False)
    # default_password = models.CharField(max_length=50, blank=True, null=True)
    role = models.CharField(max_length=100, choices=ROLE_TYPES, default="individual account")
    is_NIN_verified = models.BooleanField(default=False)
    slug = models.CharField(max_length=400, unique=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    token = models.CharField(max_length=150, null=True, blank=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    otp_used = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
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



class AgentProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, related_name="agent", on_delete=models.CASCADE
    )
    profile_image = models.ImageField(
        upload_to="profile_images", default="avartar.png", null=True, blank=True
    )
    profession = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.first_name} profile"

    class Meta:
        verbose_name = "agent profile"
        verbose_name_plural = "agent profiles"
        ordering = ["-created_at"]



class CompanyProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, related_name="company", on_delete=models.CASCADE
    )
    profile_image = models.ImageField(
        upload_to="profile_images", default="avartar.png", null=True, blank=True
    )
    profession = models.CharField(max_length=50, null=True, blank=True)
    company = models.CharField(max_length=50, null=True, blank=True)
    parent_company = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="sub_companies"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.first_name} profile"

    class Meta:
        verbose_name = "company profile"
        verbose_name_plural = "company profiles"
        ordering = ["-created_at"]
