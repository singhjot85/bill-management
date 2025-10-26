from bma.requests.views import BillViewSet
from bma.payments.views import PublicPaymentAPI

from django.contrib import admin
from django.conf import settings
from django.urls import path, include

from rest_framework.routers import SimpleRouter, DefaultRouter

router = SimpleRouter()
if settings.DEBUG:
    router = DefaultRouter()

# router.register(r'bill', BillViewSet, basename='bill')
router.register(r'public/payments', PublicPaymentAPI, basename='public-payments')

urlpatterns = [
    path("", include('bma.core.urls')),
    path('admin/', admin.site.urls, name="admin"),    
]
urlpatterns.extend(router.urls)
