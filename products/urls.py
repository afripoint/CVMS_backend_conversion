from django.urls import path
from products.views import PlanAPIView, ProductAPIView


urlpatterns = [
    path("list/", ProductAPIView.as_view(), name="product-list"),
    path("plans/", PlanAPIView.as_view(), name="plan-list"),
]
