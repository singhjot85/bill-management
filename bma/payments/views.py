from  datetime import date

from bma.payments.models import Order, Payment, Customer
from bma.payments.serializers import ExternalOrderSerializer, ExternalPaymentSerializer
from bma.core.constants import APIRequestMethods as Method
from bma.base.utils import get_contenttype_for_payment, add_rendered_pdf_to_response
from bma.requests.serializers import PublicBillSerializer

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
    BILL_TEMPLATE_NAME = 'basic_bill.html'


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

        payment = self._create_payment(order, customer, payment_mode)

        from bma.payments.client import api_key
        data = {
            "payload": {
                "key": api_key,
                "amount": order.amount,
                "currency": order.currency,
                "name": customer.name,
                "description": order.details,
                "order_id": order.exteranal_order_id,
                "callback_url": "/verify"
            },
            "id": payment.id
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
    
    @action(detail=False, methods=['post'])
    def generate_bill(self, request: Request, *args, **kwargs):

        if request.method != Method.POST.value:
            return HttpResponse({}, status=APIStatus.HTTP_400_BAD_REQUEST)
        
        order_id = request.data.get("order_id", None)
        customer_id = request.data.get("user_id", None)
        payment_id = request.data.get("payment_id", None)

        data = self._get_bill_data(order_id, customer_id, payment_id)

        response: HttpResponse = add_rendered_pdf_to_response(template='basic_bill.html', data=data, response=HttpResponse())
        return response

    def _get_bill_data(self, order_id, customer_id, payment_id):
        order: Order = Order.objects.get(id=order_id)
        payment: Payment = Payment.objects.get(id=payment_id)
        customer: Customer = Customer.objects.get(id=customer_id)

        data = {
            "organization_name": "Org Pvt. Ltd.",
            "organization_address": "38 B, Cawasji Patel Street, Fort, Mumbai",
            "name": customer.name,
            "email": customer.email,
            "country_code": customer.country_code,
            "phone_number": customer.phone_number,
            "invoice_date": date.today(),
            "today": date.today(),
            "currency": order.currency,
            "amount": order.amount,
            "total": order.amount,
            "org_email": "org@mail.com",
            "org_country_code": "+91",
            "org_phone_number": "12345 12345"
        }

        serializer = PublicBillSerializer(data=data)
        if serializer.is_valid():
            return serializer.validated_data
        else:
            return serializer.errors
    
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
    
    @action(detail=False, methods=['post'])
    def test_template(self, request):
        payment_id = '0567013a-c4c2-4aa9-881a-7bc86b243923'
        order_id = 'f523ef33-7cf4-4b5e-93f3-7dfe4a15dbf2'
        customer_id = '029ff08f-acbc-46e1-807f-579ff35c9155'

        data = self._get_bill_data(order_id, customer_id, payment_id)

        response: HttpResponse = add_rendered_pdf_to_response(
            template='basic_bill.html', 
            data=data, 
            response=HttpResponse(),
            enhanced_styling=True
        )
        
        return HttpResponse(content=response, status=APIStatus.HTTP_201_CREATED)