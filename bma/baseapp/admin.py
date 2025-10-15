from bma.baseapp.models import BaseUserModel

from django.contrib import admin


@admin.register(BaseUserModel)
class BaseUserModelAdmin(admin.ModelAdmin):
    CUSTOMER_DETAILS_FIELDSET = {
        "fields": ["user", "contact_country_code", "contact"]
    }
    TIMESTAMP_FIELDSET = {
        "classes": ["collapse"],
        "fields": ["created", "modified", "is_removed"]
    }

    list_display = (
        "id",
        "user",
        "contact_country_code",
        "contact",
        "created",
        "modified",
        "is_removed",
    )
    list_filter = ("contact_country_code", "is_removed", "created", "modified")
    search_fields = ("user__username", "user__email", "contact")
    readonly_fields = ("created", "modified", "is_removed")

    
    fieldsets = [
        ["Customer Details", CUSTOMER_DETAILS_FIELDSET],
        ["Timestamps", TIMESTAMP_FIELDSET]
    ]

    def save_model(self, request, obj, form, change):
        """
        Optional: Ensure contact is cleaned before saving in admin as well.
        """
        obj.contact = obj.contact.replace("-", "").replace(" ", "").strip()
        super().save_model(request, obj, form, change)
