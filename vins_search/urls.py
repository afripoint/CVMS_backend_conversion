from django.urls import path

from vins_search.views import (
    SingleMultiVinSearchAPIView,
    UploadFileAPIView,
    UploadMultiVinsAPIView,
    VINSearchHistoryDetailAPIView,
    VINSearchHistoryListAPIView,
)


urlpatterns = [
    path(
        "single-multi-search/",
        SingleMultiVinSearchAPIView.as_view(),
        name="multi_search",
    ),
    path("multi-upload-search/", UploadMultiVinsAPIView.as_view(), name="multi_search"),
    path("data-upload/", UploadFileAPIView.as_view(), name="upload-vin"),
    path(
        "certificate/<str:vin>/",
        VINSearchHistoryDetailAPIView.as_view(),
        name="vin-search-detail",
    ),
    path(
        "search-history/",
        VINSearchHistoryListAPIView.as_view(),
        name="vin-search-histories",
    ),
    # path("get-all-uploads/", GetAllUploadsAPIView.as_view(), name="get-all-uploads"),
]
