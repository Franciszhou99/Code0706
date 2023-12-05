from django.urls import include, path
from app_api import urls as app_api_urls
from web import urls as web_urls

urlpatterns = [
    path('app_api/', include(app_api_urls)),
    path('web/', include(web_urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]