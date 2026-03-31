import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path
from app.consumers import DashboardConsumer   # 👈 apna app name dal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": URLRouter([
        path("ws/dashboard/", DashboardConsumer.as_asgi()),
    ]),
})
