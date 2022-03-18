from decimal import Decimal
from django.http import JsonResponse

from carts.models import Cart, CartItem
from carts.api.utils import getProductObj
from orders.models import Order, OrderItem

def convertNewLengths(request):
    # for cart in Cart.objects.all():
    #     for cartItem in cart.cartitem_set.all():
    #         if cartItem.product_length and cartItem.product_length.length:
    #             cartItem.length = cartItem.product_length.length
    #             cartItem.save()
    
    for order in Order.objects.all():
        for orderItem in order.orderitem_set.all():
            if orderItem.product_length and orderItem.product_length.length:
                orderItem.length = orderItem.product_length.length
                orderItem.save()
    

    return JsonResponse({"state": "success"})
