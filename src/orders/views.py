from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.views.generic import ListView, DetailView
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail, BadHeaderError

from billing.models import BillingProfile
from .models import Order

import datetime
from decimal import Decimal


class OrderListView(LoginRequiredMixin, ListView):

    def get_queryset(self):
        return Order.objects.by_request(self.request).not_created()


class OrderDetailView(LoginRequiredMixin, DetailView):

    def get_object(self):
        qs = Order.objects.by_request(self.request).filter(
            order_id=self.kwargs.get('order_id'))
        if qs.count() == 1:
            return qs.first()
        raise Http404


def email_customer(request):
    # TODO - Uncomment below line and remove ryanjohndunne@gmail.com email address
    # this will then send to the users email instead of mine
    # to_email = request.GET.get('to_email', None)
    to_email = 'ryanjohndunne@gmail.com'
    from_email = request.GET.get('from_email', None)
    subject = request.GET.get('subject', None)
    message = request.GET.get('message', None)
    order_id = request.GET.get('order_id', None)
    order = Order.objects.get(order_id=order_id)

    try:
        send_mail(subject, message, from_email,
                  [to_email, ])
    except BadHeaderError:
        return HttpResponse("Invalid header found.")

    time_now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    order.last_email = message + '\n' + 'Sent: ' + time_now
    order.email_sent = True
    order.save()

    data = {
        'last_email': order.last_email
    }

    return JsonResponse(data)