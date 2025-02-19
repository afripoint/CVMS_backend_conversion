from rest_framework import serializers
from .models import CustomDutyFile, CustomDutyFileUploads, VINUpload, VinSearchHistory
import os
import qrcode
import base64
import uuid



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


class VinSearchHistorySerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    vin = serializers.SerializerMethodField()
    qr_code_base64 = serializers.SerializerMethodField()
    

    class Meta:
        model = VinSearchHistory
        fields = ["user", "vin", "cert_num", "qr_code_base64", "created_at"]

    def get_qr_code_base64(self, obj):
        if obj.qr_code_binary:
            return f"data:image/png;base64,{base64.b64encode(obj.qr_code_binary).decode('utf-8')}"
        return None

    def get_user(self, obj):
        return {"full_name": f"{obj.user.first_name} {obj.user.last_name},"}

    def get_vin(self, obj):
        return {
            "vin": obj.vin.vin,
            "brand": obj.vin.brand,
            "vehicle_year": obj.vin.vehicle_year,
            "vehicle_type": obj.vin.vehicle_type,
            "payment_status": obj.vin.payment_status,
            "origin_country": obj.vin.origin_country,
        }
