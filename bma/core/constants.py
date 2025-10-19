from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _

class CountryCodeChoices(TextChoices):
    INDIA = "+91", _("India - (+91)")
    NEW_YORK= "+1", _("New York - (+1)")
    # CANADA= "+1", _("CANADA - (+1)")
