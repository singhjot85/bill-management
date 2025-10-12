from bma.requests.views import BillViewSet

from django.contrib import admin
from django.conf import settings
from django.urls import path

from rest_framework.routers import SimpleRouter, DefaultRouter

router = SimpleRouter()
if settings.DEBUG:
    router = DefaultRouter()

router.register(r'bill', BillViewSet, basename='bill')

urlpatterns = [
    path('admin/', admin.site.urls),    
]
urlpatterns.extend(router.urls)
