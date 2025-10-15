from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _

class PaymentModeChoices(TextChoices):

    CARD = "card", _("Card")
    INTERNET_BANKING = "netbanking", _("Internet Banking")
    WALLET = "wallet", _("E- Wallet")
    EMI = "emi", _("EMI")
    UPI = "upi", _("UPI")
    CARDLESS_EMI = "cardless_emi", _("Cardless Emi")
    PAYLATER = "paylater", _("Paylater")


class CardNetworkChoices(TextChoices):
    VISA="visa", _("Visa")
    MASTERCARD="mastercard", _("Mastercard")
    AMEX="amex", _("American Express")
    BAJAJ="bajaj", _("Bajaj")
    MAESTRO="maestro", _("Maestro")
    RUPAY="rupay", _("Rupay")
    DINERS="diners", _("Diners")

class CardlessEMIProviderChoices(TextChoices):
    ICIC = "icic", _("ICICI Bank")
    IDFB = "idfb", _("IDFC Bank")
    HDFC = "hdfc", _("HDFC Bank")
    KKKBK = "kkbk", _("Kotak Bank")
    AXIOS = "axio", _("walnut369")
    FIBE = "earlysalary", _("Fibe")
    ZESTMONEY = "zestmoney", _("ZestMoney")
