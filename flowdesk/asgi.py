import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack   # ✅ ADD THIS
from django.core.asgi import get_asgi_application
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowdesk.settings')

django_asgi_app = get_asgi_application()

from core.consumers import DashboardConsumer

application = ProtocolTypeRouter({
    "http": django_asgi_app,

    "websocket": AuthMiddlewareStack(   # ✅ CHANGE HERE
        URLRouter([
            path("ws/dashboard/", DashboardConsumer.as_asgi()),
        ])
    ),
})
