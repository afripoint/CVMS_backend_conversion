from django.urls import path

from verifications.views import CACVerificationRequestAPIView, NINVerificationAPIView


urlpatterns = [
    path("nin/", NINVerificationAPIView.as_view(), name="verify_nin"),
    path("cac/", CACVerificationRequestAPIView.as_view(), name="verify_cac"),
]
