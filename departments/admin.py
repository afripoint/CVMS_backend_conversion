from django.contrib import admin

from departments.models import Department


class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ("department",)


admin.site.register(Department, CompanyProfileAdmin)
