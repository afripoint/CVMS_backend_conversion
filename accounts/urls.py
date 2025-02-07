from django.urls import path
from accounts.views import (
    CreateSubUserView,
    DeactivateActivateSubAccountCompanyAPIView,
    ForgetPasswordAPIView,
    LoginAPIView,
    NINVerificationAPIView,
    PasswordTokenCheck,
    RegistrationAPIView,
    ResendOTPView,
    SetNewPasswordAPIView,
    SubAccountCompanyDetailAPIView,
    SubAccountCompanyListAPIView,
    VerifyOTPAPIView,
)


urlpatterns = [
    path("register/", RegistrationAPIView.as_view(), name="register"),
    path("verify-otp/", VerifyOTPAPIView.as_view(), name="verify_otp"),
    path("resend-otp/", ResendOTPView.as_view(), name="resend_otp"),
    path("create/sub-account/", CreateSubUserView.as_view(), name="create_sub_account"),
    path(
        "detail/sub-account/<slug:slug>/",
        SubAccountCompanyDetailAPIView.as_view(),
        name="detail_sub_account",
    ),
    path("list/sub-account/", SubAccountCompanyListAPIView.as_view(), name="list_sub_account"),
    path(
        "deactivate-activate/sub-account/<slug:slug>/",
        DeactivateActivateSubAccountCompanyAPIView.as_view(),
        name="deactivate_activate_sub_account",
    ),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("verify-nin/", NINVerificationAPIView.as_view(), name="verify_nin"),
    path(
        "forget-password-email/",
        ForgetPasswordAPIView.as_view(),
        name="forget-password-email",
    ),
    path(
        "reset-password-token-check/<str:uidb64>/<str:token>/",
        PasswordTokenCheck.as_view(),
        name="reset-password-token-check"
    ),
     path(
        "set-new-password/",
        SetNewPasswordAPIView.as_view(),
        name="set-new-password/",
    ),
]
