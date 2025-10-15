from django.contrib import admin, messages

from bma.payments.client import RazorPayClient
from bma.payments.models import (
    Payment, 
    Order,
    PaymentMode,
    CardDetails
)

@admin.action(description="Generate multiple orders")
def generate_multiple_order_id(modeladmin, request, queryset):

    if len(queryset) < 1:
        messages.error(request, "ERROR - No objects selcted !!")
    
    try:
        for obj in queryset:
            client = RazorPayClient(obj)
            response = client.create_order()
            if response["is_success"]:
                messages.success(request, f"Order Created in core for [{obj}]")
    except Exception as exc:
        error_msg = str(exc)
        messages.error(request, f"ERROR occurred generating order {error_msg}")

    
@admin.action(description="Genrate single order")
def generate_order_id(modeladmin, request, queryset):
    
    if len(queryset) > 1:
        messages.error(request, "ERROR - Mutliple objects selcted !!")
    if len(queryset) < 1:
        messages.error(request, "ERROR - No objects selcted !!")
    
    try:
        obj = queryset.first()
        client = RazorPayClient(obj)
        response = client.create_order()
        if response["is_success"]:
            messages.success(request, f"Order Created in core for [{obj}]")

    except Exception as exc:
        error_msg = str(exc)
        messages.error(request, f"ERROR occurred generating order {error_msg}")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "reciept_number",
        "amount",
        "currency",
        "order_state",
        "payment_state",
        "partial_payment",
        "created",
        "modified",
    )
    list_filter = (
        "order_state",
        "payment_state",
        "currency",
        "partial_payment",
        "created",
    )
    search_fields = (
        "reciept_number",
        "order_id",
        "description",
    )
    readonly_fields = (
        "order_state",
        "payment_state",
        "reciept_number",
        "order_id",
        "created",
        "modified",
    )

    actions = [
        generate_order_id,
        generate_multiple_order_id
    ]
    fieldsets = (
        ("Order Tracking", {
            "fields": ("order_state", "payment_state")
        }),
        ("Payment Details", {
            "fields": ("amount", "currency", "partial_payment")
        }),
        ("Identifiers", {
            "fields": ("reciept_number", "order_id")
        }),
        ("Extra Info", {
            "fields": ("description", "responses", "details")
        }),
        ("Timestamps", {
            "classes": ("collapse",),
            "fields": ("created", "modified")
        }),
    )

    def has_delete_permission(self, request, obj=None):
        """
        Optional: Disable delete if you want to keep order history permanent.
        """
        return False

admin.site.register(Payment)
admin.site.register(PaymentMode)
admin.site.register(CardDetails)
