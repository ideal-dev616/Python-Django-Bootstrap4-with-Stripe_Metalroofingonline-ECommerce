from decimal import Decimal
from django.http import JsonResponse

from carts.models import Cart, CartItem
from products.models import Product


def removeFromCart(request):
    try:
        cart_obj = Cart.objects.get(cart_session_id=request.session.session_key)
        cart_item = CartItem.objects.filter(id=request.POST.get('product_id')).first()
        cart_obj.total -= round(Decimal(cart_item.line_price), 2)

        for item in cart_obj.cartitem_set.all():
            if item.product.id == cart_item.product.id and item.colour == cart_item.colour and item.length == cart_item.length:
                item.quantity = 0
                item.delete()
                continue
        cart_obj.save()

        # if cart_obj.total < 0:
        #     cart_obj.total = 0
        # if len(cart_obj.cartitem_set.all()) <= 1:
        #     cart_obj.total = 0
        # cart_obj.save()

        # cart_item.delete()

        cartData = []
        cartCount = 0
        for item in cart_obj.cartitem_set.all():
            cartData.append({
                "pk": item.pk,
                "line_price": round(item.line_price, 2),
                "quantity": item.quantity,
                "length": item.length if item.length else None
            })
            cartCount += item.quantity
        
        if cartCount >= 0:
            request.session['cart_items'] = cartCount
        else:
            cartCount = 0
            request.session['cart_items'] = 0

        data = {
            "added": False,
            "removed": True,
            "cartItemCount": cartCount,
            "items": cartData,
            "total": round(cart_obj.total, 2),
        }

        return JsonResponse(data)
    except:
        data = {
            'valid': 'error',
            'errors': 'Sorry, something went wrong removing your product',
        }
        return JsonResponse(data)
