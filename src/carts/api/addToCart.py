import re

from decimal import Decimal
from django.utils import timezone
from django.http import JsonResponse
from django.core.exceptions import MultipleObjectsReturned

from products.models import Product, Colour, AdditionalDropDown
from carts.models import Cart, CartItem
from carts.api.utils import getProductObj, getColourObj, getAdditionalObj, getStateSelected, getQuantity, getLength, getCustomLength, getLengthPrice, get_additional_price, calculate_item_price

def returnName(cart_item):
    return cart_item.product.vic_title

def addToCart(request):
    # try:
    productObj = getProductObj(request)
    colourObj = getColourObj(request)
    additionalObj = getAdditionalObj(request)
    stateSelected = getStateSelected(request)
    quantity = getQuantity(request)
    length = getLength(request)

    if stateSelected == None:
        data = {
            'valid': 'error',
            'errors': "Can't determine your state, please reselect at the top of the page",
        }
        return JsonResponse(data)

    if len(productObj.colouroption_set.all()) > 0 and colourObj == None:
        data = {
            'valid': 'error',
            'errors': 'Please select a colour from the dropdown or with the colour picker squares',
        }
        return JsonResponse(data)

    try:
        cart_obj, new_obj = Cart.objects.get_or_create(cart_session_id=request.session.session_key)
    except MultipleObjectsReturned:
        cart_obj = Cart.objects.filter(cart_session_id=request.session.session_key).first()

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart_obj,
        product=productObj,
        colour=colourObj,
        length=length,
        additional_drop_down=additionalObj,
    )

    # Calculate Cart_item price
    cart_item.price = calculate_item_price(cart_item, stateSelected)
    cart_item.quantity += int(quantity)
    cart_item.line_price = round(Decimal(cart_item.price) * Decimal(cart_item.quantity), 2)

    if cart_item.line_price <= 0:
        data = {
            'valid': 'error',
            'errors': "There was a problem calculating the price, please contact us on 1300 886 944 to finish your order",
        }
        return JsonResponse(data)
    else:
        cart_item.save()

    # Upcate cart total
    cart_obj.total = cart_obj.calculateTotal()
    if created:
        cart_obj.created = timezone.now()
    cart_obj.save()

    # Set number of items in the cart
    cart_count = 0
    for item in cart_obj.cartitem_set.all():
        cart_count += int(item.quantity)

    if cart_count >= 0:
        request.session['cart_items'] = cart_count
    else:
        cart_count = 0
        request.session['cart_items'] = 0

    cartData = []
    for item in cart_obj.cartitem_set.all():
        cartData.append({
            "pk": item.pk,
            "line_price": round(item.line_price, 2),
            "quantity": item.quantity,
            "length": item.length if item.length else None
        })

    data = {
        "added": True,
        "removed": False,
        "cartItemCount": cart_count,
        "items": cartData,
        "total": round(cart_obj.total, 2),
    }

    return JsonResponse(data, status=200)
    # except:
    #     data = {
    #         'valid': 'error',
    #         'errors': 'Sorry, something went wrong adding your product',
    #     }
    #     return JsonResponse(data)