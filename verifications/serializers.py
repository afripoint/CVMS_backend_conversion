from rest_framework import serializers
from verifications.models import CACUserVerification
import os


# NIN SERIALIZERS
class NINVerificationSerializer(serializers.Serializer):
    nin = serializers.CharField(max_length=11, min_length=11, required=True)


def validate_file_extension(file):
    """Validate file type (PNG, JPG, PDF) and size (max 10MB)"""
    valid_extensions = [".png", ".jpg", ".jpeg", ".pdf"]
    ext = os.path.splitext(file.name)[1].lower()  # Get file extension
    max_size = 10 * 1024 * 1024  # 10MB
    if ext not in valid_extensions:
        raise serializers.ValidationError("Only PNG, JPG, and PDF files are allowed.")

    if file.size > max_size:
        raise serializers.ValidationError("File size must not exceed 10MB.")


class CACVerificationSerializers(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    cac_certificate = serializers.FileField(
        validators=[validate_file_extension], required=True
    )
    status_certificate = serializers.FileField(
        validators=[validate_file_extension], required=True
    )
    letter_of_authorization = serializers.FileField(
        validators=[validate_file_extension], required=True
    )

    class Meta:
        model = CACUserVerification
        fields = (
            "email",
            "cac_certificate",
            "status_certificate",
            "letter_of_authorization",
        )
