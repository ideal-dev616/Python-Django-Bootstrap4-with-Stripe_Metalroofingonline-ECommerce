from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils.http import is_safe_url

from .models import BillingProfile, Card

import stripe
STRIPE_SECRET_KEY = getattr(settings, "STRIPE_SECRET_KEY", 'error')
STRIPE_PUB_KEY = getattr(settings, "STRIPE_PUB_KEY", 'error')

def payment_method_view(request):

    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    if not billing_profile:
        return redirect("/cart")
    next_url = None
    next_ = request.GET.get('next')
    if is_safe_url(next_, request.get_host()):
        next_url = next_
    return render(request, 'billing/payment-method.html', {"publish_key": STRIPE_PUB_KEY, "next_url": next_url})


def payment_method_createview(request):
    try:
        if request.method == "POST" and request.is_ajax():
            billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
            if not billing_profile:
                return HttpResponse({"message": "Cannot find this user"}, status_code=401)
            token = request.POST.get("token")
            if token is not None:
                new_card_obj = Card.objects.add_new(billing_profile, token)
            return JsonResponse({"message": "Success! Your card was added."})
    except stripe.error.CardError:
        return JsonResponse({"message": "Insufficient Funds"})

    return HttpResponse("error", status_code=401)


def stripe_charge(checkoutForm, order, billing_profile):
    stripe.api_key = STRIPE_SECRET_KEY

    try:
        charge = stripe.Charge.create(
            amount=int(order.owed * 100),
            currency='aud',
            description=str(order.billing_profile.email),
            source=checkoutForm.cleaned_data['stripe_token']
        )

        return True, order.owed, None

    except stripe.error.CardError as e:
        body = e.json_body
        error = body.get('error', {})

        print("Status is: %s" % e.http_status)
        print("Type is: %s" % error.get('type'))
        print("Code is: %s" % error.get('code'))
        # param is '' in this case
        print("Param is: %s" % error.get('param'))
        print("Message is: %s" % error.get('message'))

        return False, 0, str(error.get('message'))
    return False, 0


    # c = stripe.Charge.create(
    #     amount=int(order_obj.total * 100),  # 39.19 --> 3919
    #     currency="aud",
    #     metadata={"order_id": order_obj.order_id},
    # )