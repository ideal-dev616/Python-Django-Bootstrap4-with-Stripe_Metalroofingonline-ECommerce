from django.test import TestCase
from django.utils import timezone
from django.conf import settings

from decimal import *
from datetime import datetime

from xero import Xero
from xero.auth import PrivateCredentials

XERO_RSA_KEY = getattr(settings, "XERO_RSA_KEY", 'error')
XERO_CONSUMER_KEY = getattr(settings, "XERO_CONSUMER_KEY", 'error')
XERO_SECRET_KEY = getattr(settings, 'XERO_SECRET_KEY', 'error')


def account_code_selector(item, state_selected):
    # Check if the product is a flashing
    # flashings = False
    # for category in item.product.categoryoption_set.all():
    #     if category == 'Flashings':
    #         flashings = True
    #         break

    flashings = False

    if state_selected == 'VIC' and flashings:
        # 239 is the code for in house flashings
        return "239"
    elif state_selected == 'ACT':
        return "NSW"
    elif state_selected == 'NSW':
        return "NSW"
    elif state_selected == 'NT':
        return "NT"
    elif state_selected == 'QLD':
        return "QLD"
    elif state_selected == 'SA':
        return "SA"
    elif state_selected == 'TAS':
        return "TAS"
    elif state_selected == 'VIC':
        return "VIC"
    elif state_selected == 'WA':
        return "WA"


def get_account_code(order_obj):
    if order_obj.payment_type == 'Paypal':
        return '120'

    return 'STRIPE'


class XeroTestCase(TestCase):

    def test_new_invoice(self):
        with open(XERO_RSA_KEY) as keyfile:
            rsa_key = keyfile.read()
        consumer_key = XERO_CONSUMER_KEY
        consumer_secret = XERO_SECRET_KEY

        state_selected = "VIC"
        item = "nothing"
        price = 90.53
        quantity = 5

        credentials = PrivateCredentials(consumer_key, rsa_key)
        # xero = Xero(credentials, unit_price_4dps=True)
        xero = Xero(credentials)
        time = datetime.now()

        print(str(Decimal(price) / Decimal(1.1)))

        invoice = {
            "Type": "ACCREC",
            "CurrencyCode": "AUD",
            "Contact": {"Name": "Ryan Dunne", "EmailAddress": "ryanjohndunne@gmail.com"},
            "Date": datetime(time.year, time.month, time.day),
            "DueDate": datetime(time.year, time.month, time.day),
            "LineItems": [
                {
                    "Description": "Description" + "\n" \
                                   + "Colour: BLUE" \
                                   + "Length: 1.00" \
                                   + "Additional: None",
                    "Quantity": "25",
                    "UnitAmount": str(Decimal(price) / Decimal(1.1)),
                    "AccountCode": account_code_selector(item, state_selected),
                    # "TaxAmount": str(round(Decimal(price) / Decimal(11))),
                    "TaxType": "OUTPUT",
                },
            ],
            "Status": "AUTHORISED",
        }

        invoice['LineItems'].append(
            {
                "Description": "Shipping: " + "3a Haughton Street blah blah",
                "Quantity": "1",
                "UnitAmount": str(Decimal(17.99) / Decimal(1.1)),
                "AccountCode": "654",
                "TaxType": "OUTPUT",
            }
        )

        new_invoice = xero.invoices.put(invoice)

        return new_invoice
