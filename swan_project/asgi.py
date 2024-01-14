"""
ASGI config for swan_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path

from swan_project import consumers
import swan_project


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swan_project.settings')


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            [
                swan_project.routing.websocket_urlpatterns
            ]
        )
    ),
})
