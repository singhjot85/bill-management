from bma.payments.models import Order, Payment
from bma.payments.serializers import OrderSerializer, PaymentSerializer

from django.shortcuts import render
from django.http.response import HttpResponse
from rest_framework import viewsets

class BaseOrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializers = OrderSerializer

    def list(self, request, *args, **kwargs):
        return HttpResponse("Method not allowed")
    
    def destroy(self, request, *args, **kwargs):
        return HttpResponse("Method not allowed")

class BasePaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializers = PaymentSerializer

    def list(self, request, *args, **kwargs):
        return HttpResponse("Method not allowed")
    
    def destroy(self, request, *args, **kwargs):
        return HttpResponse("Method not allowed")

class BasePageViewSet(viewsets.ViewSet):
    DEFAULT_DATA_CAPTURE_TEMPLATE = ""

    def get(self, request, *args, **kwargs):
        template_name = self.DEFAULT_DATA_CAPTURE_TEMPLATE
        context = {}
        return render(request, template_name=template_name, context=context)