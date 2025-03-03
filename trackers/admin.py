from django.contrib import admin

from trackers.models import Consignment


@admin.register(Consignment)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = (
        "bill_of_ladding",
        "shipping_company",
        "hs_code",
        "port_of_load",
        "port_of_entry",
        "created_at",
    )
    list_display_links = (
        "bill_of_ladding",
        "shipping_company",
        "created_at",
    )
