from decimal import Decimal

from carts.models import Cart, CartItem
from products.models import Product, Colour, AdditionalDropDown

def getProductObj(request):
    if request.POST.get('product_id'):
        try:
            return Product.objects.filter(id=request.POST.get('product_id')).first()
        except:
            return None
    else:
        return None


def getColourObj(request):
    if request.POST.get('colour'):
        try:
            return Colour.objects.filter(colour=request.POST.get('colour')).first()
        except:
            return None
    else:
        return None


def getAdditionalObj(request):
    if request.POST.get('additional'):
        additional_option = request.POST.get('additional')
        return AdditionalDropDown.objects.filter(title=additional_option).first()
    else:
        return None


def getStateSelected(request):
    if request.POST.get('state_selected'):
        return request.POST.get('state_selected')
    else:
        return None


def getQuantity(request):
    if request.POST.get('quantity'):
        return request.POST.get('quantity')
    else:
        return None


def getLength(request):
    if request.POST.get('custom_length'):
        return request.POST.get('custom_length')
    elif request.POST.get('length'):
        return request.POST.get('length')
    else:
        return None


def getCustomLength(request):
    if request.POST.get('custom_length'):
        return (request.POST.get('custom_length') / 10000)
    else:
        return None


def getLengthPrice(cart_item, state_selected):
    length_price = 0

    if cart_item.length and Decimal(cart_item.length) > Decimal(1):
        length = cart_item.length
    else:
        length = 1

    # TAS -- Length Costs
    if state_selected == "TAS" and length != 1:
        length_price = (Decimal(length) * Decimal(1000)) * Decimal(cart_item.product.wa_price_per_mm)
    elif state_selected == "TAS" and length == 1:
        length_price = cart_item.product.vic_price
    # NSW / ACT -- Length costs
    elif (state_selected == "NSW" or state_selected == "ACT") and length != 1:
        length_price = (Decimal(length) * Decimal(1000)) * Decimal(cart_item.product.nsw_price_per_mm)
    elif (state_selected == "NSW" or state_selected == "ACT") and length == 1:
        length_price = cart_item.product.nsw_price
    # QLD -- Length costs
    elif state_selected == "QLD" and length != 1:
        length_price = (Decimal(length) * Decimal(1000)) * Decimal(cart_item.product.qld_price_per_mm)
    elif state_selected == "QLD" and length == 1:
        length_price = cart_item.product.qld_price
    # VIC / WA / NT / SA / Anything else -- Length costs
    elif length != 1:
        length_price = (Decimal(length) * Decimal(1000)) * Decimal(cart_item.product.vic_price_per_mm)
    else:
        length_price = cart_item.product.vic_price

    return round(length_price, 2)


def get_additional_price(cart_item):
    additional_price = 0
    try:
        additional_price = cart_item.additional_drop_down.additional_cost
    except AttributeError:
        pass

    return additional_price


def calculate_item_price(cart_item, stateSelected):
    # Default to Victoria if no selection
    if not stateSelected:
        return False

    length_price = getLengthPrice(cart_item, stateSelected)
    additional_price = get_additional_price(cart_item)

    price = Decimal(length_price) + Decimal(additional_price)

    return price