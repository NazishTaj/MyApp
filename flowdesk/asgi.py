import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path

# ✅ FIRST: settings set karo
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowdesk.settings')

# ✅ SECOND: Django init karo
django_asgi_app = get_asgi_application()

# ✅ THIRD: ab import karo
from core.consumers import DashboardConsumer

application = ProtocolTypeRouter({
    "http": django_asgi_app,

    "websocket": URLRouter([
        path("ws/dashboard/", DashboardConsumer.as_asgi()),
    ]),
})
