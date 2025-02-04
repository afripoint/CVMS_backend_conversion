from django.urls import path
from accounts.views import NINVerificationAPIView, RegistrationAPIView


urlpatterns = [
    path("register/", RegistrationAPIView.as_view(), name="register"),
    path("verify-nin/", NINVerificationAPIView.as_view(), name="verify_nin"),
]
