from django.urls import path

from data_uploads.views import UploadFileAPIView

urlpatterns = [
    path("data-upload/", UploadFileAPIView.as_view(), name="upload-vin"),
    # path("get-all-uploads/", GetAllUploadsAPIView.as_view(), name="get-all-uploads"),
]
