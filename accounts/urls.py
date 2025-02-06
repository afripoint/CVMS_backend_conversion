from django.urls import path
from accounts.views import (
    LoginAPIView,
    NINVerificationAPIView,
    RegistrationAPIView,
    ResendOTPView,
    VerifyOTPAPIView,
)


urlpatterns = [
    path("register/", RegistrationAPIView.as_view(), name="register"),
    path("verify-otp/", VerifyOTPAPIView.as_view(), name="verify_otp"),
    path("resend-otp/", ResendOTPView.as_view(), name="resend_otp"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("verify-nin/", NINVerificationAPIView.as_view(), name="verify_nin"),
]
