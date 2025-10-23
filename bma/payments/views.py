from bma.payments.models import Order, Payment, Customer
from bma.payments.serializers import ExternalOrderSerializer, ExternalPaymentSerializer
from bma.core.constants import APIRequestMethods as Method
from bma.base.utils import get_contenttype_for_payment

from django.http.response import HttpResponse

from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status as APIStatus
from rest_framework.decorators import action
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer

class PublicPaymentAPI(viewsets.ViewSet):
    """
    This will be a public endpoint and login won't be required for this
    """
    authentication_classes = []
    permission_classes = []
    template_name = 'public_datacapture.html'
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]


    def list(self, request: Request, *args, **kwargs):
        response = {}

        order_id = request.query_params.get("pk", None)
        if not order_id:
            order = None
            payment = None
            serializer = ExternalOrderSerializer()
            paymt_serializer = ExternalPaymentSerializer()
        else:
            order = Order.objects.get(id=order_id)
            payment = order.payments.first()
            serializer = ExternalOrderSerializer(order)
            paymt_serializer = ExternalPaymentSerializer(payment)

        response = {
            'order_serializer': serializer,
            'payment_serializer': paymt_serializer,
            'order': order,
            'payment': payment
        }

        return Response(response, status=APIStatus.HTTP_200_OK)

    def create(self, request: Request, *args, **kwargs):
        order_id = request.data.get("order_id", None)
        customer_id = request.data.get("user_id", None)
        payment_mode = request.data.get("payment_mode", None)
        print(payment_mode)

        if not (order_id and customer_id and payment_mode):
            return Response({}, status=APIStatus.HTTP_400_BAD_REQUEST)

        order: Order = Order.objects.get(id=order_id)
        customer: Customer = Customer.objects.get(id=customer_id)

        self._create_payment(order, customer, payment_mode)

        from bma.payments.client import api_key
        data = {
            "key": api_key,
            "amount": order.amount,
            "currency": order.currency,
            "name": customer.name,
            "description": order.details,
            "order_id": order.exteranal_order_id,
            "callback_url": "/verify"
        }

        return Response(data, status=APIStatus.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def create_user(self, request: Request, *args, **kwargs):
        if request.method != Method.POST.value:
            return HttpResponse({}, status=APIStatus.HTTP_400_BAD_REQUEST)
        
        user, _ = Customer.objects.get_or_create(
            name= request.data.get('name'),
            email= request.data.get('email'),
            country_code = request.data.get('country_code'),
            phone_number= request.data.get('phone_number')
        )

        return Response(data={"id": str(user.id)}, status=APIStatus.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def create_order(self, request: Request, *args, **kwargs):
        if request.method != Method.POST.value:
            return HttpResponse({}, status=APIStatus.HTTP_400_BAD_REQUEST)
        
        order, _ = Order.objects.get_or_create(
            currency = request.data.get("currency"),
            amount = request.data.get("amount"),
            description = request.data.get("description")
        )

        return Response(data={"id": str(order.id)}, status=APIStatus.HTTP_201_CREATED)
    
    def _create_payment(self, order, customer, payment_mode):
        content_type, Model = get_contenttype_for_payment(payment_mode)
        object = Model.objects.create()

        payment , _ = Payment.objects.get_or_create(
            order= order,
            requested_by= customer,
            payment_mode = payment_mode,
            content_type = content_type,
            object_id= str(object.id)
        )
        return payment
    
    def _generate_bill(self):
        pass