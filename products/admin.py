from django.contrib import admin

from products.models import Plan, Product


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "is_plan_based",
        "is_active",
    )
    list_display_links = (
        "name",
        "price",
    )


admin.site.register(Product, ProductAdmin)


class PlansAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "vin_allocation",
        "is_active",
    )
    list_display_links = (
        "name",
        "price",
    )


admin.site.register(Plan, PlansAdmin)
