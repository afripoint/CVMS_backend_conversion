from django.urls import path

from trackers.views import (
    ConsignmentAPIView,
    ConsignmentStatusAPIView,
    GetTeaserAPIVIew,
    TrackingIDGenerateAPIView,
)

urlpatterns = [
    path("get-teaser/", GetTeaserAPIVIew.as_view(), name="get-teaser"),
    path("get-consignment/", ConsignmentAPIView.as_view(), name="get-consignment"),
    path(
        "generate_tracking_id/<slug:slug>/",
        TrackingIDGenerateAPIView.as_view(),
        name="update-tracking-id",
    ),
    path(
        "status/<str:bill_of_ladding>/",
        ConsignmentStatusAPIView.as_view(),
        name="consignment-status",
    ),
]
