from rest_framework import serializers
from .models import CustomDutyFile, CustomDutyFileUploads, VINUpload
import os


class CustomDutyUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomDutyFile
        fields = "__all__"


class CustomDutyFileUploadsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomDutyFileUploads
        fields = (
            "uploaded_by",
            "file_name",
            "file",
            "file_type",
            "processed_status",
            "slug",
            "uploaded_at",
        )


class VinSerializer(serializers.ModelSerializer):
    # vin = serializers.CharField(required=True)

    class Meta:
        model = CustomDutyFile
        fields = (
            "vin",
            "brand",
            "model",
            "vehicle_year",
            "engine_type",
            "vreg",
            "vehicle_type",
            "payment_status",
        )


class VINUploadSerializer(serializers.Serializer):
    vins = serializers.FileField(required=True)

    def validate_file_extension(file):
        """Validate file type (xlsx, csv) and size (max 10MB)"""
        # valid_extensions = [".xlsx", ".csv"]
        # ext = os.path.splitext(file.name)[1].lower()  # Get file extension
        max_size = 10 * 1024 * 1024  # 10MB
        # if ext not in valid_extensions:
        #     raise serializers.ValidationError("Only csv, and csv files are allowed.")

        if file.size > max_size:
            raise serializers.ValidationError("File size must not exceed 10MB.")
