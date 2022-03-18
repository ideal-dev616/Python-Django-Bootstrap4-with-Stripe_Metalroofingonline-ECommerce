from decimal import Decimal
from django.http import JsonResponse

from datetime import datetime, timedelta

from carts.models import Cart, CartItem
from carts.api.utils import getProductObj
from orders.models import Order, OrderItem

def removeCarts(request):
    # for cartItem in CartItem.objects.all():
    #     if not cartItem.cart:
    #         cartItem.delete()
    
    for cart in Cart.objects.all():
        insertion_date = cart.created
        insertion_date = cart.created.replace(tzinfo=None)
        time_between_insertion = datetime.now() - insertion_date
        if time_between_insertion.days>60:
            for item in cart.cartitem_set.all():
                item.delete()
            cart.delete()

    return JsonResponse({"state": "success"})
