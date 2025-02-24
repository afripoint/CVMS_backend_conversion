from django.contrib import admin
from vins_search.models import CustomDutyFile, CustomDutyFileUploads

@admin.register(CustomDutyFile)
class CustumDutyFilesAdmin(admin.ModelAdmin):
    list_display = (
        "vin",
        "brand",
        "model",
        "vehicle_year",
        "engine_type",
        "vreg",
        "vehicle_type",
        "importer_tin",
        "importer_business_name",
        "importer_address",
        "origin_country",
        "hscode",
        "sgd_num",
        "sgd_date",
        "office_cod",
        "payment_status",
    )

    list_display_links = (
        "vin",
        "brand",
        "model",
    )

@admin.register(CustomDutyFileUploads)
class CustomDutyUploadsAdmin(admin.ModelAdmin):
    list_display = (
        "uploaded_by",
        "file_name",
        "file",
        "file_type",
        "processed_status",
        "uploaded_at",
    )
    list_display_links = ("uploaded_by",)


