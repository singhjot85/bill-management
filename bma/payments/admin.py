from django.contrib import admin
from bma.payments.models import Payment, Order

admin.site.register(Payment)
admin.site.register(Order)
