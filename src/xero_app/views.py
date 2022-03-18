import re, os
from django.conf import settings
from django.http.response import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from decimal import *
from datetime import datetime

from xero.api import Payroll
from carts.models import Cart, CartItem
from shipping.models import Suburb
from xero_app.utils import account_code_selector

from xero import Xero
from xero.auth import OAuth2Credentials
from xero.constants import XeroScopes
from django.http import HttpResponseRedirect
from django.core.cache import cache
from dotenv import load_dotenv
from os.path import join, dirname
import json

dotenv_path = join(dirname(dirname(__file__)), '.env')
load_dotenv(dotenv_path=dotenv_path)

client_id = os.getenv('client_id')
client_secret = os.getenv('client_secret')
callback_uri = os.getenv('callback_uri')
log_file = os.getenv('MRO_LOG_FILE')

if not log_file:
    log_file = 'log.txt'


# On the server the print function is unreliable, so we redirect to a file
def print(*args):
    with open(log_file, 'a') as f:
        for data in args:
            f.write(str(data))
        f.write('\n')
    return


def save_creds(xero_creds):
    creds_file=open(join(dirname(dirname(dirname(__file__))), '.creds'),'w')
    creds_file.write(xero_creds)
    creds_file.close()


def read_creds():
    with open(join(dirname(dirname(dirname(__file__))), '.creds'),'r') as creds_file:
        return creds_file.read()

def stateSupplierTitle(customerState, item):
    if customerState == 'NSW' or customerState == 'ACT' and item.product.nsw_supplier_title != None:
        if hasattr(item.product, 'nsw_supplier_title'):
            return item.product.nsw_supplier_title
    elif customerState == 'WA' and item.product.wa_supplier_title != None:
        if hasattr(item.product, 'wa_supplier_title'):
            return item.product.wa_supplier_title
    elif customerState == 'QLD' and item.product.qld_supplier_title != None:
        if hasattr(item.product, 'qld_supplier_title'):
            return item.product.qld_supplier_title
    else:
        if hasattr(item.product, 'vic_supplier_title') and item.product.vic_supplier_title != None:
            return item.product.vic_supplier_title
    
    return item.product.title


def cart_invoice_create(request):
    name = request.POST.get('name')
    phone_number = request.POST.get('phone_number')
    email = request.POST.get('email')
    pickup = request.POST.get('pickup')
    postage_standard = request.POST.get('postage_standard')
    postage_express = request.POST.get('postage_express')
    address = request.POST.get('address')
    suburb = request.POST.get('suburb')
    postcode = request.POST.get('postcode')
    state = request.POST.get('state')
    billing_address = request.POST.get('billing_address')
    billing_suburb = request.POST.get('billing_suburb')
    billing_postcode = request.POST.get('billing_postcode')
    billing_state = request.POST.get('billing_state')
    billing_same = request.POST.get('billing_same')
    pk = request.POST.get('pk')
    shipping_price = 0

    # If not pickup, add price
    if address != '48 Watt Rd':
        try:
            shipping = Suburb.objects.filter(postal_code=postcode).first()
            shipping_price = shipping.delivery_price
        except:
            pass

    try:
        cart_obj = Cart.objects.get(pk=pk)
    except:
        print("ERROR CART")
        data = {
            'error': 'Cart no longer exists'
        }
        return JsonResponse(data, status=500)
    
    time = datetime.now()

    invoice = {
        "Type": "ACCREC",
        "CurrencyCode": "AUD",
        "Contact": 
            {
                "Name": str(name) + " " + str(phone_number),
                "EmailAddress": str(email),
                "Addresses": [{
                    "AddressType": "STREET",
                    "AddressLine1": str(billing_address) + ", " + str(billing_state),
                    "City": str(billing_suburb),
                    "PostalCade": str(billing_postcode),
                }]
            },
        "Date": int(datetime(time.year, time.month, time.day).timestamp()),
        "DueDate": int(datetime(time.year, time.month, time.day).timestamp()),
        "LineAmountTypes": "Inclusive",
        "LineItems": [
            {
                "Description": re.sub('[®]', '', stateSupplierTitle(state, item)) + "\n" \
                    + ("Colour: " + item.colour.colour + "\n" if item.colour else "") \
                    + ("Length: " + str(item.length) + "\n" if item.length else "") \
                    + ("Additional: " + item.additional_drop_down.title if item.additional_drop_down else ""),
                "Quantity": item.quantity,
                "UnitAmount": str(round(Decimal(item.price), 2)),
                "AccountCode": account_code_selector(item, state),
                "TaxType": "OUTPUT",
            } for item in cart_obj.cartitem_set.all()
        ],
        "Status": "AUTHORISED",
    }


    if postage_express == 'true':
        invoice['LineItems'].append(
            {
                "Description": "Delivery: " + str(address) + ", " + str(suburb) + ", " + str(postcode) + ", " + str(state),
                "Quantity": "1",
                "UnitAmount": str(Decimal(25.99)),
                "TaxType": "OUTPUT",
                "AccountCode": "654"
            }
        )
    elif postage_standard == 'true':
        invoice['LineItems'].append(
            {
                "Description": "Delivery: " + str(address) + ", " + str(suburb) + ", " + str(postcode) + ", " + str(state),
                "Quantity": "1",
                "UnitAmount": str(Decimal(17.99)),
                "TaxType": "OUTPUT",
                "AccountCode": "654"
            }
        )
    elif shipping_price > 0:
        invoice['LineItems'].append(
            {
                "Description": "Delivery: " + str(address) + ", " + str(suburb) + ", " + str(postcode) + ", " + str(state),
                "Quantity": "1",
                "UnitAmount": str(Decimal(shipping_price)),
                "TaxType": "OUTPUT",
                "AccountCode": "654"
            }
        )
    elif address == "48 Watt Rd":
        invoice['LineItems'].append(
            {
                "Description": "Pickup: " + str(address) + ", " + str(suburb) + ", " + str(postcode) + ", " + str(state),
                "Quantity": "1",
                "UnitAmount": "0",
                "TaxType": "OUTPUT",
                "AccountCode": "654"
            }
        )
    else:
        invoice['LineItems'].append(
            {
                "Description": "Shipping To Undefined Postcode: " + str(address) + ", " + str(suburb) + ", " + str(postcode) + ", " + str(state),
                "Quantity": "1",
                "UnitAmount": "0",
                "TaxType": "OUTPUT",
                "AccountCode": "654"
            }
        )

    # cache.set('invoice', invoice)
    request.session['invoice'] = invoice
    print("invoice = ", request.session.get('invoice', False)  )
    callback_uri = os.getenv('callback_uri')
    cred_state = read_creds()
    print("cred_state = #" + cred_state + "#" )
    try:
        json.loads(cred_state)

    except json.decoder.JSONDecodeError:
        print("NOT")
        credentials = OAuth2Credentials(client_id, client_secret, callback_uri=callback_uri,
            # scope=[XeroScopes.OFFLINE_ACCESS, XeroScopes.ACCOUNTING_CONTACTS,
            #         XeroScopes.ACCOUNTING_TRANSACTIONS]
            scope=[ 
                XeroScopes.PAYROLL_PAYRUNS,
                XeroScopes.OPENID,
                XeroScopes.PAYROLL_SETTINGS,
                XeroScopes.PROJECTS,
                XeroScopes.ACCOUNTING_ATTACHMENTS,
                XeroScopes.EMAIL,
                XeroScopes.ACCOUNTING_CONTACTS,
                XeroScopes.PAYROLL_PAYSLIP,
                XeroScopes.PAYROLL_EMPLOYEES,
                XeroScopes.PROFILE,
                XeroScopes.ASSETS,
                XeroScopes.ACCOUNTING_ATTACHMENTS_READ,
                XeroScopes.ACCOUNTING_REPORTS_READ,
                XeroScopes.FILES,
                XeroScopes.ACCOUNTING_SETTINGS,
                XeroScopes.ACCOUNTING_JOURNALS_READ,
                XeroScopes.ACCOUNTING_TRANSACTIONS, 
                XeroScopes.PAYROLL_TIMESHEETS, 
                XeroScopes.OFFLINE_ACCESS,
            ]
        )
        authorization_url = credentials.generate_url()
        # cache.set('xero_creds', credentials.state)
        save_creds(json.dumps(credentials.state))
        data = {
            'success': 'success',
            'authorization_url': authorization_url
        }

        return JsonResponse(data)

    else:    
        print("YES")    
        return HttpResponseRedirect('/xero/callback-view')


def process_callback_view(request):
    print("read_creds() = ", read_creds())    
    cred_state = json.loads(read_creds())
    print("cred_state = ", cred_state)
    # invoice = cache.get('invoice')  
    invoice = request.session.get('invoice', False)  
    if "Date" in invoice:
        invoice["Date"] = datetime.fromtimestamp(int(invoice["Date"]))
    if "DueDate" in invoice:
        invoice["DueDate"] = datetime.fromtimestamp(int(invoice["DueDate"]))
    print("== invoice = ", invoice )
    print("== 2")
    credentials = OAuth2Credentials(**cred_state)
    print("== credentials = ", credentials.token)

    try:
        if credentials.expired():
            print("== 4")
            credentials.refresh()
            save_creds(json.dumps(credentials.state))
    except:
        print("== 5")
        auth_secret = request.get_raw_uri()
        print("== 6")
        credentials.verify(auth_secret)
        print("== 7")
        credentials.set_default_tenant()
        print("== 8")
        save_creds(json.dumps(credentials.state))
    xero = Xero(credentials)

    print("== 9")
    new_invoice = xero.invoices.put(invoice)
    data = {
        'success': 'no_redirect',
    }

    return JsonResponse(data)



