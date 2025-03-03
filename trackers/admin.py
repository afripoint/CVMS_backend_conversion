from django.contrib import admin

from trackers.models import Consignment


@admin.register(Consignment)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = (
        "bill_of_ladding",
        "registration_officer",
        "shipping_company",
        "importer_phone",
        "hs_code",
        "port_of_loading",
        "port_of_landing",
        "created_at",
    )
    list_display_links = (
        "bill_of_ladding",
        "registration_officer",
        "shipping_company",
    )
