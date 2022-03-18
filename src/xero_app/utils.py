import re, os, json

from django.conf import settings
from django.utils import timezone

from decimal import *
from datetime import datetime

from xero import Xero
from xero.auth import OAuth2Credentials
from django.core.cache import cache
from dotenv import load_dotenv
from os.path import join, dirname

XERO_RSA_KEY = getattr(settings, "XERO_RSA_KEY", 'error')
XERO_CONSUMER_KEY = getattr(settings, "XERO_CONSUMER_KEY", 'error')
XERO_SECRET_KEY = getattr(settings, 'XERO_SECRET_KEY', 'error')


def read_creds():
    with open(join(dirname(dirname(dirname(__file__))), '.creds'),'r') as creds_file:
        return creds_file.read()


def save_creds(xero_creds):
    creds_file=open(join(dirname(dirname(dirname(__file__))), '.creds'),'w')
    creds_file.write(xero_creds)
    creds_file.close()


def stateSupplierTitle(customerState, item):
    if customerState == 'NSW' or customerState == 'ACT' and item.product.nsw_supplier_title != None:
        if hasattr(item.product, 'nsw_supplier_title'):
            return item.product.nsw_supplier_title
        else: 
            return item.product.title
    elif customerState == 'WA' and item.product.wa_supplier_title != None:
        if hasattr(item.product, 'wa_supplier_title'):
            return item.product.wa_supplier_title
        else: 
            return item.product.title
    elif customerState == 'QLD' and item.product.qld_supplier_title != None:
        if hasattr(item.product, 'qld_supplier_title'):
            return item.product.qld_supplier_title
        else: 
            return item.product.title
    else:
        if hasattr(item.product, 'vic_supplier_title') and item.product.vic_supplier_title != None:
            return item.product.vic_supplier_title
        else: 
            return item.product.title
    
    return item.product.title

def account_code_selector(item, state_selected):

    # Check if the product is a flashing
    flashings = False
    for category in item.product.categoryoption_set.all():
        if category == 'Flashings':
            flashings = True
            break

    if state_selected == 'VIC' and flashings:
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

    return

def get_account_code(order_obj):
    if order_obj.payment_type == 'PayPal' or order_obj.payment_type == 'Paypal':
        return '120'

    return 'STRIPE'

def xero_invoice(order_obj, state_selected):
    cred_state = json.loads(read_creds())
    if not cred_state:
        return "NO_LOGIN"
    
    credentials = OAuth2Credentials(**cred_state)
    if credentials.expired():
           credentials.refresh()
           #cache.set('xero_creds', credentials.state)
           save_creds(json.dumps(credentials.state))

    xero = Xero(credentials)
    time = datetime.now()

    invoice = {
        "Type": "ACCREC",
        "CurrencyCode": "AUD",
        "Contact": 
            {
                "Name": str(order_obj.shipping_address.get_name()) + " " + str(order_obj.shipping_address.phone_number),
                "EmailAddress": str(order_obj.billing_profile.email)
            },
        "Date": datetime(time.year, time.month, time.day),
        "DueDate": datetime(time.year, time.month, time.day),
        "LineAmountTypes": "Inclusive",
        "LineItems": [
            {
                "Description": re.sub('[®]', '', stateSupplierTitle(state_selected, item)) + "\n" \
                    + ("Colour: " + item.colour.colour + "\n" if item.colour else "") \
                    + ("Length: " + str(item.length) + "\n" if item.length else "") \
                    + ("Additional: " + item.additional_drop_down.title if item.additional_drop_down else ""),
                "Quantity": item.quantity,
                "UnitAmount": str(round(Decimal(item.price), 2)),
                "AccountCode": account_code_selector(item, state_selected),
                "TaxType": "OUTPUT",
            } for item in order_obj.orderitem_set.all()
        ],
        "Status": "AUTHORISED",
    }

    # Add shipping cost to invoice
    if order_obj.shipping_total > 0:
        invoice['LineItems'].append(
            {
                "Description": "Shipping: " + str(order_obj.shipping_address.get_address()),
                "Quantity": "1",
                "TaxType": "OUTPUT",
                "UnitAmount": str(round(Decimal(order_obj.shipping_total), 2)),
                "AccountCode": "654"
            }
        )
    
    new_invoice = xero.invoices.put(invoice)

    return new_invoice


def xero_payment(order_obj, new_invoice):
    cred_state = json.loads(read_creds())
    if not cred_state:
        return "NO_LOGIN"
    
    credentials = OAuth2Credentials(**cred_state)
    if credentials.expired():
           credentials.refresh()
           #cache.set('xero_creds', credentials.state)
           save_creds(json.dumps(credentials.state))

    xero = Xero(credentials)
    time = datetime.now()

    invoiceID = new_invoice[0]['InvoiceID']
    invoice = xero.invoices.get(invoiceID)
                

    payment = {
        "Invoice": {"InvoiceID": invoiceID},
        "Account": {"Code": get_account_code(order_obj)},
        "Date": datetime(time.year, time.month, time.day, time.hour, time.minute),
        "Amount": str(invoice[0]['Total']),
    }

    new_payment = xero.payments.put(payment)

    return new_payment
