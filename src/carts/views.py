from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from django.core.exceptions import MultipleObjectsReturned
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from decimal import *
from datetime import date, datetime, timedelta

from accounts.forms import LoginForm, GuestForm
from accounts.models import GuestEmail
from addresses.forms import CheckoutForm
from addresses.models import Address
from billing.models import BillingProfile
from billing.views import stripe_charge
from orders.models import Order, OrderItem
from products.models import Product, Colour, Length, AdditionalDropDown
from .models import Cart, CartItem
from orders.models import Order
from shipping.models import Suburb, DisallowedShippingDates
from xero_app.utils import account_code_selector, get_account_code, xero_invoice, xero_payment

import googlemaps
import stripe
import json
import math

VERSION = getattr(settings, "VERSION", 'PROD')
STRIPE_SECRET_KEY = getattr(settings, "STRIPE_SECRET_KEY", 'error')
STRIPE_PUB_KEY = getattr(settings, "STRIPE_PUB_KEY", 'error')
GOOGLE_API_KEY = getattr(settings, "GOOGLE_API_KEY", 'error')
stripe.api_key = STRIPE_SECRET_KEY
STANDARD_POSTAGE = 17.99
WA_STANDARD_POSTAGE = 20.99
EXPRESS_POSTAGE = 25.99
WA_EXPRESS_POSTAGE = 28.99
# When rounding decimal to two places
TWOPLACES = Decimal(10) ** -2

def saved_cart(request):
    print("== saved cart")
    used_email = request.GET.get("email", None)
    order_obj = Order.objects.select_related('cart').filter(billing_profile__email=used_email, cart_id__isnull=False).first()
    
    if order_obj != None:
        cart_id = order_obj.cart_id
        request.session['cart_id'] = cart_id

        old_session_key = Cart.objects.filter(pk=cart_id).first().cart_session_id

        if old_session_key != request.session.session_key:
            Cart.objects.filter(cart_session_id=request.session.session_key).delete()
            Cart.objects.filter(pk=cart_id).update(cart_session_id=request.session.session_key)
        
        # Set number of items in the cart
        cart_count = 0
        cartitem_obj = CartItem.objects.filter(cart_id=cart_id)
        for item in cartitem_obj:
            cart_count += int(item.quantity)

        if cart_count >= 0:
            request.session['cart_items'] = cart_count
        else:
            cart_count = 0
            request.session['cart_items'] = 0
        
        return redirect("cart:checkout")

    else:
        return redirect("home")
    
    

    

    # qs = self.get_queryset().filter(id=cart_id)
    # if qs.count() == 1:
    #     new_obj = False
    #     cart_obj = qs.first()
    #     if request.user.is_authenticated and cart_obj.user is None:
    #         cart_obj.user = request.user
    #         cart_obj.save()
    # else:
    #     cart_obj = Cart.objects.new(user=request.user)
    #     new_obj = True
    #     request.session['cart_id'] = cart_obj.id
    # return cart_obj, new_obj


def checkout_done_view(request):
    try:
        order_obj = Order.objects.get(order_id=request.session['order_id'])
        del request.session['order_id']
        request.session.modified = True
    except:
        order_obj = None

    # Clear session based values
    request.session['cart_items'] = 0
    request.session['order_id'] = None
    # Cart has previously been set to none so that order doesn't get deleted on cart delete
    try:
        Cart.objects.filter(
            cart_session_id=request.session.session_key).delete()
    except:
        pass

    context = {
        "object": order_obj,
        "api_key": settings.GOOGLE_API_KEY
    }

    return render(request, "carts/checkout-done.html", context)


def create_shipping_address(request, checkoutForm):
    try:
        address, created = Address.objects.get_or_create(
            first_name=checkoutForm.cleaned_data['first_name'],
            last_name=checkoutForm.cleaned_data['last_name'],
            phone_number=checkoutForm.cleaned_data['phone_number'],
            address_type='Shipping address',
            address_line_1=checkoutForm.cleaned_data['address_line_1'],
            city=checkoutForm.cleaned_data['city'],
            state=checkoutForm.cleaned_data['state'],
            postal_code=checkoutForm.cleaned_data['postal_code'],
        )

        address.save()

        return address

    except:
        address = Address.objects.filter(
            first_name=checkoutForm.cleaned_data['first_name'],
            last_name=checkoutForm.cleaned_data['last_name'],
            phone_number=checkoutForm.cleaned_data['phone_number'],
            address_type='Shipping address',
            address_line_1=checkoutForm.cleaned_data['address_line_1'],
            city=checkoutForm.cleaned_data['city'],
            state=checkoutForm.cleaned_data['state'],
            postal_code=checkoutForm.cleaned_data['postal_code'],
        ).first()

    return address


def create_billing_address(request, checkoutForm):
    try:
        address, created = Address.objects.get_or_create(
            first_name=checkoutForm.cleaned_data['billing_first_name'],
            last_name=checkoutForm.cleaned_data['billing_last_name'],
            phone_number=checkoutForm.cleaned_data['billing_phone_number'],
            address_type='Billing address',
            address_line_1=checkoutForm.cleaned_data['billing_address_line_1'],
            city=checkoutForm.cleaned_data['billing_city'],
            state=checkoutForm.cleaned_data['billing_state'],
            postal_code=checkoutForm.cleaned_data['billing_postal_code'],
            country=checkoutForm.cleaned_data['billing_country'],
        )
        address.save()

    except:
        address = Address.objects.filter(
            first_name=checkoutForm.cleaned_data['billing_first_name'],
            last_name=checkoutForm.cleaned_data['billing_last_name'],
            phone_number=checkoutForm.cleaned_data['billing_phone_number'],
            address_type='Billing address',
            address_line_1=checkoutForm.cleaned_data['billing_address_line_1'],
            city=checkoutForm.cleaned_data['billing_city'],
            state=checkoutForm.cleaned_data['billing_state'],
            postal_code=checkoutForm.cleaned_data['billing_postal_code'],
            country=checkoutForm.cleaned_data['billing_country'],
        ).first()

    return address


def shipping_cost(request, postage, address):
    shipping_type = ''
    shipping_cost = 0

    if address.address_line_1 == '48 Watt Rd' and address.city == 'Mornington':
        shipping_cost = 0
        shipping_type = 'Pickup'
    elif postage == 'standard':
        if request.session['state_selected'] == 'WA':
            shipping_cost = WA_STANDARD_POSTAGE
            shipping_type = 'WA Standard Post'
        else:
            shipping_cost = STANDARD_POSTAGE
            shipping_type = 'Standard Post'
    elif postage == 'express':
        if request.session['state_selected'] == 'WA':
            shipping_cost = WA_EXPRESS_POSTAGE
            shipping_type = 'WA Express Post'
        else:
            shipping_cost = EXPRESS_POSTAGE
            shipping_type = 'Express Post'
    else:
        try:
            suburb = Suburb.objects.get(postal_code=address.postal_code)
            shipping_cost = suburb.delivery_price
            shipping_type = str(request.session['state_selected'])
        except MultipleObjectsReturned:
            suburb = Suburb.objects.filter(
                postal_code=address.postal_code).first()
            shipping_cost = suburb.delivery_price
            shipping_type = str(request.session['state_selected'])
        except:
            data = {
                'valid': 'stripe_error',
                'errors': 'Sorry, something went wrong when calculating your shipping. Please contact us on 1300 886 944 to finalise your order.',
            }
            return JsonResponse(data)

    if shipping_cost <= 0 and shipping_type != 'Pickup':
        return 0, 'False'

    return shipping_cost, shipping_type


def cartitem_to_orderitem(cart_obj, order):
    for item in cart_obj.cartitem_set.all():
        line_price = Decimal(item.price) * Decimal(item.quantity)
        order_item, created = OrderItem.objects.get_or_create(product=item.product, order=order, colour=item.colour,
                                                              length=item.length, quantity=item.quantity,
                                                              price=item.price,
                                                              line_price=line_price,
                                                              additional_drop_down=item.additional_drop_down)
        order_item.save()

    return


def get_billing_address(request, checkoutForm):
    # If billing address is different from normal address create new
    if checkoutForm.cleaned_data['billing_first_name']:
        billing_address = create_billing_address(request, checkoutForm)
    else:
        billing_address = create_shipping_address(request, checkoutForm)

    return billing_address


def get_delivery_date(request, checkoutForm):
    if checkoutForm.cleaned_data['delivery_date'] == 'ASAP':
        delivery_date = 'ASAP'
        return 'ASAP'
    elif checkoutForm.cleaned_data['delivery_date']:
        try:
            delivery_date = datetime.strptime(
                checkoutForm.cleaned_data['delivery_date'][:-44], '%a %b %d %Y %X')
            delivery_date = delivery_date.strftime('%d/%m/%y')
        except:
            delivery_date = checkoutForm.cleaned_data['delivery_date']

        return delivery_date

    return 'No Date'


def process_order(request, checkoutForm):
        # ORDER.SHIPPING_TYPE SET TO WHERE IT'S GOING
    email = checkoutForm.cleaned_data['email']
    address = create_shipping_address(request, checkoutForm)
    cart_obj = Cart.objects.filter(
        cart_session_id=request.session.session_key).first()
    billing_address = get_billing_address(request, checkoutForm)
    delivery_date = get_delivery_date(request, checkoutForm)
    postage = checkoutForm.cleaned_data['postage']

    # Order Creation (tax/subtotal/total calculated on save)
    order, created = Order.objects.get_or_create(cart=cart_obj)
    order.shipping_address = Address.objects.get(pk=address.pk)
    order.billing_address = Address.objects.get(pk=billing_address.pk)

    try:
        order.shipping_total, order.shipping_type = shipping_cost(
            request, postage, address)
    except:
        print("Error: Line 232 carts/views.py")
        data = {
            'valid': 'stripe_error',
            'errors': 'Sorry, something went wrong when calculating your shipping. Please contact us on 1300 886 944 to finalise your order.',
        }
        return JsonResponse(data)

    order.delivery_date = delivery_date
    order.delivery_instructions = checkoutForm.cleaned_data['delivery_instructions']
    order.order_instructions = checkoutForm.cleaned_data['order_instructions']
    cartitem_to_orderitem(cart_obj, order)
    try:
        billing_profile, created = BillingProfile.objects.get_or_create(
            email=email)
    except MultipleObjectsReturned:
        billing_profile = BillingProfile.objects.filter(email=email).first()

    order.billing_profile = billing_profile

    return order


def validate_form_stripe(request):
    checkoutForm = CheckoutForm(request.POST or None)

    if request.POST.get('postage') == '':
        data = {
            'valid': 'form_error',
            'errors': "Sorry, we don't currently ship to your address. <br>Please call us on 1300 886 944 or email us at sales@metalroofingonline and we can help!"
        }
        return JsonResponse(data)

    

    if not checkoutForm.is_valid():
        data = {
            'valid': 'form_error',
            'errors': str(checkoutForm.errors),
        }

        return JsonResponse(data)

    # try:
    order = process_order(request, checkoutForm)
    order.save()
    # except:
    #     data = {
    #         'valid': 'stripe_error',
    #         'errors': 'Sorry, something went wrong when calculating your shipping. Please contact us on 1300 886 944 to finalise your order.',
    #     }
    #     return JsonResponse(data)

    # try:
    if order.shipping_type == 'False':
        data = {
            'valid': 'stripe_error',
            'errors': 'Sorry, something went wrong when calculating your shipping. Please contact us on 1300 886 944 to finalise your order.',
        }
        return JsonResponse(data)
    # except:
    #     data = {
    #         'valid': 'stripe_error',
    #         'errors': 'Sorry, something went wrong when calculating your shipping. Please contact us on 1300 886 944 to finalise your order.',
    #     }
    #     return JsonResponse(data)

    order.cart = None
    order.save()

    # Stripe payment
    if checkoutForm.cleaned_data['stripe_token'] and order.owed > 0:
        charged, amount, errors = stripe_charge(
            checkoutForm, order, order.billing_profile)
        if charged:
            order.paid = amount
            order.mark_paid
            order.status = 'Payment Accepted'
            order.payment_type = 'Stripe'
            order.save()
        else:
            data = {
                'valid': 'stripe_error',
                'errors': errors,
            }

            return JsonResponse(data)
    elif order.owed <= 0:
        # Clear session based values
        request.session['cart_items'] = 0
        Cart.objects.filter(
            cart_session_id=request.session.session_key).delete()

        data = {
            'valid': 'stripe_error',
            'errors': 'Sorry, something went wrong. Please contact us to solve your issue with code: ORDER_PAID OR 0 for order number: ' + str(
                order.order_id),
        }

        return JsonResponse(data)

    # Xero invoice + payment on invoice
    try:
        state_selected = order.shipping_address.state
    except:
        data = {
            'valid': 'stripe_error',
            'errors': 'Unable to calculate shipping for your suburb please refresh the page and try again. If that doesnt work, please contact us to finish your order.',
        }

        return JsonResponse(data)

    # if VERSION == 'PROD':
    new_invoice = xero_invoice(order, state_selected)
    new_payment = xero_payment(order, new_invoice)

    # Confirmation email of the order
            
    send_order_email(order)
    
    # Clear session based values
    request.session['cart_items'] = 0
    # Cart has previously been set to none so that order doesn't get deleted on cart delete
    Cart.objects.filter(cart_session_id=request.session.session_key).delete()

    request.session['order_id'] = order.order_id
    request.session.modified = True

    data = {
        "valid": 'true',
    }

    return JsonResponse(data)


def validate_form_paypal(request):
    checkoutForm = CheckoutForm(request.POST or None)

    if not checkoutForm.is_valid():
        data = {
            'valid': 'form_error',
            'errors': str(checkoutForm.errors),
        }

        return JsonResponse(data)

    try:
        order = process_order(request, checkoutForm)
    except:
        data = {
            'valid': 'stripe_error',
            'errors': 'Sorry, something went wrong when calculating your shipping. Please contact us on 1300 886 944 to finalise your order.',
        }
        return JsonResponse(data)

    try:
        if order.shipping_type == 'False':
            data = {
                'valid': 'stripe_error',
                'errors': 'Sorry, something went wrong when calculating your shipping. Please contact us on 1300 886 944 to finalise your order.',
            }

            return JsonResponse(data)
    except:
        data = {
            'valid': 'stripe_error',
            'errors': 'Sorry, something went wrong when calculating your shipping. Please contact us on 1300 886 944 to finalise your order.',
        }
        return JsonResponse(data)

    order.save()

    if order.owed <= 0:
        # Clear session based values
        request.session['cart_items'] = 0
        Cart.objects.filter(
            cart_session_id=request.session.session_key).delete()

        data = {
            'valid': 'stripe_error',
            'errors': 'Sorry, something went wrong. Please contact us to solve your issue with code: ORDER_PAID for order number: ' + str(
                order.order_id),
        }

        return JsonResponse(data)

    request.session['order_id'] = order.order_id
    request.session.modified = True

    data = {
        "valid": 'true',
    }

    return JsonResponse(data)


def validate_form_cart(request):
    checkoutForm = CheckoutForm(request.POST or None)
    if request.POST.get('postage') == '':
        data = {
            'valid': 'form_error',
            'errors': "Sorry, we don't currently ship to your address. <br>Please call us on 1300 886 944 or email us at sales@metalroofingonline and we can help!"
        }
        return JsonResponse(data)

    if not checkoutForm.is_valid():
        data = {
            'valid': 'form_error',
            'errors': str(checkoutForm.errors),
        }

        return JsonResponse(data)

    # try:
    order = process_order(request, checkoutForm)
    order.save()
    # except:
    #     data = {
    #         'valid': 'stripe_error',
    #         'errors': 'Sorry, something went wrong when calculating your shipping. Please contact us on 1300 886 944 to finalise your order.',
    #     }
    #     return JsonResponse(data)

    # try:
    if order.shipping_type == 'False':
        data = {
            'valid': 'stripe_error',
            'errors': 'Sorry, something went wrong when calculating your shipping. Please contact us on 1300 886 944 to finalise your order.',
        }
        return JsonResponse(data)
    # except:
    #     data = {
    #         'valid': 'stripe_error',
    #         'errors': 'Sorry, something went wrong when calculating your shipping. Please contact us on 1300 886 944 to finalise your order.',
    #     }
    #     return JsonResponse(data)

    # order.cart = None
    order.save()

    # # Stripe payment
    # if checkoutForm.cleaned_data['stripe_token'] and order.owed > 0:
    #     charged, amount, errors = stripe_charge(
    #         checkoutForm, order, order.billing_profile)
    #     if charged:
    #         order.paid = amount
    #         order.mark_paid
    #         order.status = 'Payment Accepted'
    #         order.payment_type = 'Stripe'
    #         order.save()
    #     else:
    #         data = {
    #             'valid': 'stripe_error',
    #             'errors': errors,
    #         }

    #         return JsonResponse(data)
    # elif order.owed <= 0:
    #     # Clear session based values
    #     request.session['cart_items'] = 0
    #     Cart.objects.filter(
    #         cart_session_id=request.session.session_key).delete()

    #     data = {
    #         'valid': 'stripe_error',
    #         'errors': 'Sorry, something went wrong. Please contact us to solve your issue with code: ORDER_PAID OR 0 for order number: ' + str(
    #             order.order_id),
    #     }

    #     return JsonResponse(data)

    # # Xero invoice + payment on invoice
    # try:
    #     state_selected = order.shipping_address.state
    # except:
    #     data = {
    #         'valid': 'stripe_error',
    #         'errors': 'Unable to calculate shipping for your suburb please refresh the page and try again. If that doesnt work, please contact us to finish your order.',
    #     }

    #     return JsonResponse(data)

    # if VERSION == 'PROD':
    #     new_invoice = xero_invoice(order, state_selected)
    #     new_payment = xero_payment(order, new_invoice)

    # Confirmation email of the order
            
    # send_order_email(order)
    
    # Clear session based values
    # request.session['cart_items'] = 0
    # # Cart has previously been set to none so that order doesn't get deleted on cart delete
    # Cart.objects.filter(cart_session_id=request.session.session_key).delete()

    request.session['order_id'] = order.order_id
    request.session.modified = True

    data = {
        "valid": 'true',
    }

    return JsonResponse(data)


def checkout_paypal(request):
    try:
        order_obj = Order.objects.get(order_id=request.session['order_id'])
    except:
        order_obj = None

    context = {
        "object": order_obj,
    }

    return render(request, "carts/checkout-paypal.html", context)


def checkout_new(request):
    try:
        cart_obj, cart_created = Cart.objects.get_or_create(
            cart_session_id=request.session.session_key)
    except MultipleObjectsReturned:
        cart_obj = Cart.objects.filter(
            cart_session_id=request.session.session_key).first()
    order_obj = Order.objects.select_related('billing_profile').select_related('shipping_address') \
        .filter(cart_id=cart_obj.id).values('id', 'billing_profile__email', 'shipping_address__first_name', \
            'shipping_address__last_name', 'shipping_address__phone_number', 'shipping_address__address_line_1', \
            'shipping_address__city', 'shipping_address__postal_code', 'shipping_address__state', 'shipping_type').first()

    
    if order_obj:
        checkout_form_data = {}
        checkout_form_data["email"] = order_obj["billing_profile__email"]
        checkout_form_data["first_name"] = order_obj["shipping_address__first_name"]
        checkout_form_data["last_name"] = order_obj["shipping_address__last_name"]
        checkout_form_data["phone_number"] = order_obj["shipping_address__phone_number"]
        checkout_form_data["autocomplete"] = "{}, {} {}, Australia".format(order_obj["shipping_address__address_line_1"], order_obj["shipping_address__city"], order_obj["shipping_address__state"])
        checkout_form_data["address_line_1"] = order_obj["shipping_address__address_line_1"]
        checkout_form_data["city"] = order_obj["shipping_address__city"]
        checkout_form_data["postal_code"] = order_obj["shipping_address__postal_code"]
        checkout_form_data["state"] = order_obj["shipping_address__state"]

        if order_obj["shipping_type"] == "WA Standard Post" or order_obj["shipping_type"] == "Standard Post":
            checkout_form_data["postage"] = "standard"
        elif order_obj["shipping_type"] == "WA Express Post" or order_obj["shipping_type"] == "Express Post":
            checkout_form_data["postage"] = "express"
        else:
            checkout_form_data["postage"] = "etc"

        checkout_form = CheckoutForm(checkout_form_data)
    
    else:
        checkout_form = CheckoutForm()


    notToday = date.today() + timedelta(days=2)
    postage = postageCheck(cart_obj)

    disabledDates = []

    # TODO, base on state selected
    try:
        state = request.session['state_selected']
    except KeyError:
        data = {
            'valid': 'error',
            'errors': "Sorry, we can't determine your state. Please contact us on 1300 886 944 for help.",
        }

        return JsonResponse(data)

    for item in DisallowedShippingDates.objects.all():
        if item.state == state or item.state == 'ALL':
            string = '%d/%d/%d' % (item.date.day,
                                   item.date.month, item.date.year)
            disabledDates.append(string)

    data = {
        'cart': cart_obj,
        'cart_count': request.session['cart_items'],
        'disabledDates': disabledDates,
        'startDate': 8,
        'checkout_form': checkout_form,
        'postage': postage,
        'publish_key': STRIPE_PUB_KEY,
        'state_selected': request.session['state_selected']
    }

    return render(request, "carts/checkout-new.html", data)


def postageCheck(cart_obj):
    postage = True

    for item in cart_obj.cartitem_set.all():
        if not item.product.postage:
            postage = False

    return postage


def delivery_options(request):
    try:
        postal_code = Suburb.objects.filter(
            postal_code=request.POST.get('postal_code')).first()

        post_code = postal_code.postal_code
        price = postal_code.delivery_price
        message = postal_code.message

    except:
        post_code = 0
        price = 0
        message = "<div class='font-weight-bold'>Your delivery address is outside our standard delivery areas but we may still be able to deliver to you. <br /> Please email us your cart number and delivery address details to <a href='mailto:sales@metalroofingonline.com.au'>sales@metalroofingonline.com.au</a> or call us on <span class='text-orange'>1300 886 944</span> for a delivery price.</div>"

    data = {
        'post_code': post_code,
        'price': price,
        'message': message,
    }

    return JsonResponse(data)


def cart_clear(request):
    for item in Cart.objects.all():
        if item.total == 0:
            item.delete()


def paypal_success(request):
    line = request.body
    order_id = line.decode('utf-8').split('=', 1)[-1]

    order_obj = Order.objects.get(order_id=request.session['order_id'])
    cart_obj = Cart.objects.get(cart_session_id=request.session.session_key)

    order_obj.mark_paid()  # sort a signal for us
    order_obj.cart = None
    order_obj.payment_type = 'PayPal'
    order_obj.status = 'Payment Accepted'
    order_obj.save()

    request.session['cart_items'] = 0

    Cart.objects.filter(cart_session_id=request.session.session_key).delete()

    state_selected = order_obj.shipping_address.state

    # if VERSION == 'PROD':
    new_invoice = xero_invoice(order_obj, state_selected)
    new_payment = xero_payment(order_obj, new_invoice)

    # Confirmation email of the order
    send_order_email(order_obj)

    data = {
        "success": 'TRUE',
    }

    return JsonResponse(data)


def cart_overlay_remove_item(request):
    """ API request to remove item from cart through the overlay-cart """
    try:
        cart_obj, new_obj = Cart.objects.get_or_create(
            cart_session_id=request.session.session_key)
    except MultipleObjectsReturned:
        cart_obj = Cart.objects.filter(
            cart_session_id=request.session.session_key).first()

    for count, item in enumerate(reversed(cart_obj.cartitem_set.all())):
        if str(item.pk) == str(request.POST.get('pk')):
            request.session['cart_items'] = request.session['cart_items'] - item.quantity
            if len(cart_obj.cartitem_set.all()) > 1:
                cart_obj.total = cart_obj.total - item.line_price
            else:
                cart_obj.total = 0
                request.session['cart_items'] = 0

            item.delete()
            cart_obj.save()
            break

    data = {
        'total': cart_obj.total,
        'cart_count': request.session['cart_items'],
    }

    return JsonResponse(data)


def cart_detail_api_view(request):
    """ API request to remove from cart """
    try:
        cart_obj, new_obj = Cart.objects.get_or_create(
            cart_session_id=request.session.session_key)
    except MultipleObjectsReturned:
        cart_obj = Cart.objects.filter(
            cart_session_id=request.session.session_key).first()

    products = []

    location = request.session.setdefault('state_selected', 'VIC')

    for count, item in enumerate(reversed(cart_obj.cartitem_set.all())):
        products.append({})
        # ID
        try:
            products[count]["id"] = item.product.id
        except AttributeError:
            pass

        # URL
        try:
            products[count]["url"] = item.product.get_absolute_url()
        except AttributeError:
            pass

        # Name
        try:
            if location == 'ACT' or location == 'NSW':
                products[count]["name"] = item.product.nsw_title
            elif location == 'QLD':
                products[count]["name"] = item.product.qld_title
            else:
                products[count]["name"] = item.product.vic_title
        except AttributeError:
            pass

        # Colour
        try:
            products[count]["colour"] = item.colour.colour
        except AttributeError:
            products[count]["colour"] = "None"

        # Length
        try:
            products[count]["length"] = item.length.length
        except AttributeError:
            products[count]["length"] = "None"

        # Additional Drop Down
        try:
            products[count][
                "additionaldropdown"] = item.additional_drop_down.title
        except AttributeError:
            products[count]["additionaldropdown"] = "None"

        # Price
        try:
            products[count]["price"] = item.price
        except AttributeError:
            pass

        # Quantity
        try:
            products[count]["quantity"] = item.quantity
        except AttributeError:
            pass

        # Image
        try:
            products[count][
                "image"] = item.product.imageoption_set.first().option.image.url
        except AttributeError:
            pass

    cart_data = {
        "products": products,
        "subtotal": cart_obj.subtotal(),
        "taxes": cart_obj.taxes(),
        "total": cart_obj.total,
    }

    return JsonResponse(cart_data)


def cart_changed_state(request):
    # Delete all cart items when user changes state
    try:
        try:
            cart = Cart.objects.get(
                cart_session_id=request.session.session_key)
        except MultipleObjectsReturned:
            cart = Cart.objects.filter(
                cart_session_id=request.session.session_key).first()
        cart.delete()

        # Cart emptied out so we want to set cart_items to 0
        request.session['cart_items'] = 0
    except Cart.DoesNotExist:
        pass

    # Set the selected state in the session so that we can calculate prices
    # off the state
    request.session['state_selected'] = request.POST.get('id', "VIC")

    context = {
        "state": request.session['state_selected'],
    }

    return JsonResponse(context)


def cart_quantity_change(request):
    # TODO - This should just be using the public key instead of finding each variable of the product
    # Get product information
    product_id = int(CartItem.objects.filter(id=request.GET.get('product_id')).first().product.id)
    
    try:
        cart_obj, cart_created = Cart.objects.get_or_create(
            cart_session_id=request.session.session_key)
    except MultipleObjectsReturned:
        cart_obj = Cart.objects.filter(
            cart_session_id=request.session.session_key).first()
    
    new_quantity = 0
    total_quantity = 0
    for item in cart_obj.cartitem_set.all():
        if item.product.id == product_id:
            if request.GET.get('subtract') == 'true':
                if item.quantity > 1:
                    item.quantity -= 1
            elif request.GET.get('add') == 'true':
                item.quantity += 1
            new_quantity = item.quantity
            item.save()
        total_quantity += item.quantity
    cart_obj.save()

    cart_data = {
        'quantity': new_quantity,
        "subtotal": cart_obj.subtotal(),
        "taxes": cart_obj.taxes(),
        "total": round(cart_obj.total, 2),
        "total_quantity": total_quantity,
    }

    return JsonResponse(cart_data)


def cart_shipping_change(request):
    order_obj = Order.objects.get(order_id=request.GET.get('order_id'))

    if request.GET.get('express') == 'true':
        order_obj.shipping_total = round(Decimal(25.99), 2)
    else:
        order_obj.shipping_total = round(Decimal(17.99), 2)

    order_obj.total = round(
        Decimal(order_obj.cart.total) + Decimal(order_obj.shipping_total), 2)
    order_obj.save()

    cart_data = {
        'shipping_total': order_obj.shipping_total,
        'order_total': order_obj.total
    }

    return JsonResponse(cart_data)


def cart_home(request):
    try:
        cart_obj, cart_created = Cart.objects.get_or_create(
            cart_session_id=request.session.session_key)
    except MultipleObjectsReturned:
        cart_obj = Cart.objects.filter(
            cart_session_id=request.session.session_key).first()

    taxes = cart_obj.taxes()
    total = cart_obj.total

    return render(request, "carts/home.html", {"cart": cart_obj, 'taxes': taxes, 'total': total})


def get_product_id(request):
    if request.POST.get('product_id'):
        return request.POST.get('product_id')
    else:
        return None


def get_remove_item(request):
    if request.POST.get('remove-item'):
        return request.POST.get('remove-item')
    else:
        return None


def get_colour_request(request):
    if request.POST.get('colour') != 'None':
        product_colour = request.POST.get('colour')
        return Colour.objects.filter(colour=product_colour).first()
    else:
        return None


# Chanded by Damian
def get_order_objects(request):
    objects = []

    if request.POST.get('custom_length', False):
        items = json.loads(request.POST.get('custom_length'))
        for row in items:
            length = row['length']
            length_obj = Length.objects.filter(length=length).first()
            if length_obj is None:
                length_obj = Length.objects.create(length=length)
            objects.append({
                'length': length_obj,
                'quantity': row['quantity']
            })

    return objects


# return length object by selected length, create lengths from custom length if not existed, and return custom lengths
def get_length(request):
    product_length = None

    # length by selected option
    if request.POST.get('length') != 'None':
        length = Decimal(request.POST.get('length'))
        product_length = Length.objects.filter(length=length).first()

    return product_length


def get_additional(request):
    if request.POST.get('additional') != 'None':
        additional_option = request.POST.get('additional')
        return AdditionalDropDown.objects.filter(title=additional_option).first()
    else:
        return None


def remove_product(request, product_id, state_selected):
    # Get the cart
    cart_obj = Cart.objects.get(cart_session_id=request.session.session_key)

    # Get the item from the cart
    cart_item = CartItem.objects.filter(id=product_id).first()

    # Remove the product from the cart
    cart_item.delete()

    cart_obj.total -= round(Decimal(cart_item.price) *
                            Decimal(cart_item.quantity), 2)
    cart_item.line_price = round(
        Decimal(cart_item.price) * Decimal(cart_item.quantity), 2)
    if cart_obj.total < 0:
        cart_obj.total = 0
    cart_obj.save()
    added = False

    return cart_obj


def add_product(request, product_id, colour_obj, length_obj, quantity, additional_obj, state_selected):
    try:
        product_obj = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return redirect("cart:home")

    try:
        cart_obj, new_obj = Cart.objects.get_or_create(
            cart_session_id=request.session.session_key)
    except MultipleObjectsReturned:
        cart_obj = Cart.objects.filter(
            cart_session_id=request.session.session_key).first()

    # create cart_item with selected length
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart_obj,
        product=product_obj,
        colour=colour_obj,
        length=length_obj,
        additional_drop_down=additional_obj,
    )

    cart_item.price = calculate_item_price(cart_item, state_selected)
    cart_item.quantity += int(quantity)
    cart_item.line_price = round(
        Decimal(cart_item.price) * Decimal(cart_item.quantity), 2)
    cart_item.save()
    added = True
    current_value = round(Decimal(cart_item.price) * Decimal(quantity), 2)
    cart_obj.total = round(Decimal(cart_obj.total) + current_value, 2)
    cart_obj.created = timezone.now()
    cart_obj.save()

    return cart_obj, cart_item


def cart_update(request):
    colour_obj = False

    # Get product information
    product_id = get_product_id(request)
    remove_item = get_remove_item(request)
    colour_obj = get_colour_request(request)
    order_objs = get_order_objects(request)
    additional_obj = get_additional(request)
    state_selected = request.session.setdefault('state_selected', 'VIC')

    cart_items = []

    # Remove or add product depending on user input
    if remove_item is not None:
        data = {
            'valid': 'error',
            'errors': 'Sorry, something went wrong when removing your product. Please contact us on 1300 886 944 for help.',
        }

        return JsonResponse(data)

        try:
            cart_obj = remove_product(request, product_id, state_selected)
        except:
            data = {
                'valid': 'error',
                'errors': 'Sorry, something went wrong when removing your product. Please contact us on 1300 886 944 for help.',
            }

            return JsonResponse(data)
        added = False
    else:
        # add products having length option
        if len(order_objs) > 0:
            for obj in order_objs:
                cart_obj, cart_item = add_product(
                    request, product_id, colour_obj, obj['length'], obj['quantity'], additional_obj, state_selected)
                added = True
                cart_items.append(cart_item)
        # add products having no length option
        else:
            cart_obj, cart_item = add_product(
                request, product_id, colour_obj, None, request.POST.get('quantity', 0), additional_obj, state_selected)
            added = True
            cart_items.append(cart_item)

    # Set number of items in the cart
    cart_count = 0
    for item in cart_obj.cartitem_set.all():
        cart_count += item.quantity

    request.session['cart_items'] = cart_count

    if remove_item is not None:
        # Asynchronous JavaScript And XML / JSON
        if request.is_ajax():
            json_data = {
                "added": added,
                "removed": not added,
                "cartItemCount": cart_count
            }
            return JsonResponse(json_data, status=200)
    else:
        # Asynchronous JavaScript And XML / JSON
        if request.is_ajax():
            data = []
            for item in cart_items:
                data.append({
                    "pk": item.pk,
                    "line_price": round(item.line_price, 2),
                    "quantity": item.quantity,
                    "length": item.length.length if item.length else None
                })

            json_data = {
                "added": added,
                "removed": not added,
                "cartItemCount": cart_count,
                "items": data,
                "total": round(cart_obj.total, 2),
            }
            return JsonResponse(json_data, status=200)

    return redirect("cart:home")


def checkout_home(request):
    cart_created = None
    order_obj = None
    try:
        cart_obj, cart_created = Cart.objects.get_or_create(
            cart_session_id=request.session.session_key)
    except MultipleObjectsReturned:
        cart_obj = Cart.objects.filter(
            cart_session_id=request.session.session_key).first()

    if cart_created or CartItem.objects.filter(cart=cart_obj).count() == 0:
        return redirect("cart:home")

    login_form = LoginForm(request=request)
    guest_form = GuestForm(request=request)
    address_form = AddressCheckoutForm()
    billing_address_id = request.session.get("billing_address_id", None)
    shipping_address_id = request.session.get("shipping_address_id", None)
    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(
        request)
    address_qs = None
    has_card = False

    if billing_profile is not None:

        if request.user.is_authenticated:
            address_qs = Address.objects.filter(
                billing_profile=billing_profile)

        order_obj, order_obj_created = Order.objects.new_or_get(
            billing_profile, cart_obj)
        order_obj.cart = cart_obj

        if shipping_address_id:
            postal_code = calculate_shipping(
                request, cart_obj, Address.objects.get(id=shipping_address_id), )
            address = Address.objects.get(id=shipping_address_id)

            # Set delivery date of order
            order_obj.delivery_date = cart_obj.delivery_date

            if address.address_line_1 == '48 Watt Rd':
                order_obj.shipping_total = Decimal(0)
                order_obj.shipping_address = Address.objects.get(
                    id=shipping_address_id)
                del request.session["shipping_address_id"]
            else:
                if postal_code == "None":
                    msg = "Unfortunately we don't currently ship to this address, or you've entered an invalid Australian address."
                    messages.error(request, msg)

                elif postal_code == "POSTAGE":
                    order_obj.shipping_total = round(17.99, 2)
                    order_obj.total = round(
                        Decimal(order_obj.cart.total) + Decimal(17.99), 2)
                    order_obj.shipping_address = Address.objects.get(
                        id=shipping_address_id)
                    del request.session["shipping_address_id"]

                elif postal_code.message:
                    msg = postal_code.message
                    messages.error(request, msg)
                else:
                    order_obj.shipping_total = round(
                        Decimal(postal_code.delivery_price), 2)
                    order_obj.total = round(
                        Decimal(order_obj.cart.total) + Decimal(postal_code.delivery_price), 2)
                    order_obj.shipping_address = Address.objects.get(
                        id=shipping_address_id)
                    del request.session["shipping_address_id"]

        if billing_address_id:
            order_obj.billing_address = Address.objects.get(
                id=billing_address_id)
            del request.session["billing_address_id"]

        order_obj.save()

        has_card = billing_profile.has_card

    taxes = round(Decimal(cart_obj.total) / Decimal(11), 2)

    if request.method == "POST":
        "check that order is done"
        is_prepared = order_obj.check_done()
        if is_prepared:
            did_charge, crg_msg = billing_profile.charge(order_obj)
            if did_charge:
                order_obj.mark_paid()  # sort a signal for us
                order_obj.status = 'Payment Accepted'
                order_obj.payment_type = 'Stripe'
                request.session['cart_items'] = 0

                order_obj.cart = None
                order_obj.save()

                for item in cart_obj.cartitem_set.all():
                    line_price = Decimal(item.price) * Decimal(item.quantity)
                    od = OrderItem(product=item.product, order=order_obj, colour=item.colour,
                                   length=item.length, quantity=item.quantity, price=item.price,
                                   line_price=line_price, additional_drop_down=item.additional_drop_down)
                    od.save()

                Cart.objects.filter(
                    cart_session_id=request.session.session_key).delete()
                request.session['order_id'] = order_obj.order_id

                if not billing_profile.user:
                    '''
                    is this the best spot?
                    '''
                    billing_profile.set_cards_inactive()
                return redirect("cart:success")
            else:
                return redirect("cart:checkout")

    is_postage = False

    context = {
        "object": order_obj,
        "billing_profile": billing_profile,
        "login_form": login_form,
        "guest_form": guest_form,
        "address_form": address_form,
        "address_qs": address_qs,
        "has_card": has_card,
        "publish_key": STRIPE_PUB_KEY,
        "taxes": taxes,
    }
    return render(request, "carts/checkout.html", context)


def calculate_shipping(request, cart_obj, address):
    postage = True

    for item in cart_obj.cartitem_set.all():
        if item.product.postage != True:
            postage = False
            break

    if postage == True:
        return "POSTAGE"
    try:
        postal_code = Suburb.objects.get(postal_code=address.postal_code)

        return postal_code
    except:
        return "None"


def calculate_distance(request, address):
    gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

    if address.address_line_2 is not None:
        destination_address = (
            str(address.address_line_1) + ", " +
            str(address.address_line_2) + ", " +
            str(address.city) + ", " +
            str(address.state) + ", " +
            str("Australia")
        )
    else:
        destination_address = (
            str(address.address_line_1) + ", " +
            str(address.city) + ", " +
            str(address.state) + ", " +
            str("Australia")
        )

    my_distance = gmaps.distance_matrix('Melbourne, 3192', destination_address)
    distance = my_distance['rows'][0]['elements'][0]['distance']['value']

    return distance


def calculate_item_price(cart_item, state_selected):
    # Default to Victoria if no selection #TODO prompt user for state
    if not state_selected:
        state_selected = 'VIC'

    colour_price = get_colour_price(cart_item)
    zincalume_discount = get_zincalume_discount(cart_item)
    length_price = get_length_price(cart_item, state_selected)
    additional_price = get_additional_price(cart_item)

    price = Decimal(length_price) + Decimal(colour_price) \
        + Decimal(additional_price) - Decimal(zincalume_discount)

    return price


def get_colour(cart_item):
    try:
        colour = cart_item.colour.colour
    except AttributeError:
        colour = None

    return colour


def get_colour_price(cart_item):
    colour_price = 0
    colour = get_colour(cart_item)

    if colour:
        colour_price = cart_item.colour.additional_cost

    return colour_price


def get_length_price(cart_item, state_selected):
    length_price = 0

    # VIC / WA / NT / SA -- Length costs
    if state_selected == "VIC" or state_selected == "WA" or state_selected == "NT" or state_selected == "SA":
        try:
            length = cart_item.length.length if cart_item.length.length > 1 else 1
            length_price = Decimal(length * 1000) * \
                cart_item.product.vic_price_per_mm
        except AttributeError:
            length_price = cart_item.product.vic_price
    # TAS -- Length Costs
    elif state_selected == "TAS":
        try:
            length = cart_item.length.length if cart_item.length.length > 1 else 1
            length_price = Decimal(length * 1000) * \
                cart_item.product.wa_price_per_mm
        except AttributeError:
            length_price = cart_item.product.vic_price
    # NSW / ACT -- Length costs
    elif state_selected == "NSW" or state_selected == "ACT":
        try:
            length = cart_item.length.length if cart_item.length.length > 1 else 1
            length_price = Decimal(length * 1000) * \
                cart_item.product.nsw_price_per_mm
        except AttributeError:
            length_price = cart_item.product.nsw_price
    # QLD -- Length costs
    elif state_selected == "QLD":
        try:
            length = cart_item.length.length if cart_item.length.length > 1 else 1
            length_price = Decimal(length * 1000) * \
                cart_item.product.qld_price_per_mm
        except AttributeError:
            length_price = cart_item.product.qld_price

    return length_price


def get_zincalume_discount(cart_item):
    colour = get_colour(cart_item)
    zincalume_discount = 0

    if colour == "ZINCALUME®":
        if not cart_item.length:
            zincalume_discount = Decimal(
                cart_item.product.zincalume_discount_victoria)
        else:
            length = cart_item.length.length if cart_item.length.length > 1 else 1
            zincalume_discount = (Decimal(
                cart_item.product.zincalume_discount_victoria) * (Decimal(length) * 1000))

    return zincalume_discount


def get_additional_price(cart_item):
    additional_price = 0
    try:
        additional_price = cart_item.additional_drop_down.additional_cost
    except AttributeError:
        pass

    return additional_price


def send_order_email(order_obj):

    msg_plain = render_to_string(
        '../templates/email/order_confirmation.txt', {'order_obj': order_obj})
    msg_html = render_to_string(
        '../templates/email/order_confirmation.html', {'order_obj': order_obj})

    subject = 'Order #' + order_obj.order_id + " confirmed."
    from_address = 'enquiries@metalroofingonline.com.au'
    recipient_list = str(order_obj.billing_profile.email)

    send_mail(subject, msg_plain, 'enquiries@metalroofingonline.com.au', [str(order_obj.billing_profile.email)],
              html_message=msg_html)

    return


def generate_paypal_items(cart_obj):
    string = ""
    for item in cart_obj.cartitem_set.all():
        string += '{' + \
                  'name: "' + str(item.product.title) + '",' + \
                  'description: "' + 'Colour: ' + str(item.colour) + ', Length: ' + str(
                      item.length) + ', Extras: ' + str(item.additional_drop_down) + '",' + \
            'quantity: "' + str(item.quantity) + '",' + \
                  'price: "' + str(round(Decimal(item.line_price), 2)) + '",' + \
                  'currency:' + "AUD" + '},'

    return string
