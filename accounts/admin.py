from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.models import (
    AgentProfile,
    CompanyProfile,
    CustomUser,
    IndividualProfile,
)


class CustomUserAmin(BaseUserAdmin):
    list_display = (
        "first_name",
        "last_name",
        "phone_number",
        "email",
        "role",
        "is_verified",
        "is_active",
        "created_at",
    )
    list_display_links = ("first_name", "last_name", "email", "phone_number")
    list_filter = ("first_name", "last_name", "phone_number")
    search_fields = ("phone_number",)
    ordering = ("-date_joined",)
    fieldsets = ()
    ordering = ("email",)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide"),
                "fields": (
                    "phone_number",
                    "first_name",
                    "last_name",
                    "email",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


@admin.register(IndividualProfile)
class IndividualProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "user",
        "created_at",
        "updated_at",
    )


@admin.register(AgentProfile)
class AgentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "agency_name",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "user",
        "created_at",
        "updated_at",
    )


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "company_name",
        "parent_company",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "profession",
        "company",
        "parent_company",
        "created_at",
        "updated_at",
    )


admin.site.register(CustomUser, CustomUserAmin)

