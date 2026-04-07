import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path
from core.consumers import DashboardConsumer   

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowdesk.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": URLRouter([
        path("ws/dashboard/<int:clinic_id>/", DashboardConsumer.as_asgi()),
    ]),
})
