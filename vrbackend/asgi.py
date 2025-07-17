import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import students.routing  # ✅ Import your app's routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vrbackend.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            students.routing.websocket_urlpatterns  # ✅ Reference to app-level routing
        )
    ),
})
