from django.urls import path
from .consumers import DashboardConsumer

websocket_urlpatterns = [
    path("ws/dashboard/<int:clinic_id>/", DashboardConsumer.as_asgi()),
]
