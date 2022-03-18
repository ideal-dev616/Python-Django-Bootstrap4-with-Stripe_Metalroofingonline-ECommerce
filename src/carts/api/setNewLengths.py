from decimal import Decimal
from django.http import JsonResponse

from products.models import Product

def createNewMaxLength(request):
    # try:
    for product in Product.objects.all():
        max_len = 0
        for length in product.lengthoption_set.all():
            if length.option and length.option.length > max_len:
                max_len = length.option.length
        product.max_length = max_len
        if max_len > 0:
            product.min_length = 1
            product.length_steps = 1
        product.save()

    return JsonResponse({"state": "success"})
    # except:

    #     return JsonResponse({"state": "failure"})
