from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, UpdateView, CreateView
from django.shortcuts import redirect
from django.utils.http import is_safe_url

from billing.models import BillingProfile
from carts.models import Cart
from .models import Address


# class AddressListView(LoginRequiredMixin, ListView):
#     template_name = 'addresses/list.html'

#     def get_queryset(self):
#         request = self.request
#         billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
#         return Address.objects.filter(billing_profile=billing_profile)


# class AddressUpdateView(LoginRequiredMixin, UpdateView):
#     template_name = 'addresses/update.html'
#     form_class = AddressForm
#     success_url = '/addresses'

#     def get_queryset(self):
#         request = self.request
#         billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
#         return Address.objects.filter(billing_profile=billing_profile)


# class AddressCreateView(LoginRequiredMixin, CreateView):
#     template_name = 'addresses/update.html'
#     form_class = AddressForm
#     success_url = '/addresses'

#     def form_valid(self, form):
#         request = self.request
#         billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
#         instance = form.save(commit=False)
#         instance.billing_profile = billing_profile
#         instance.save()
#         return super(AddressCreateView, self).form_valid(form)


# def checkout_address_create_view(request):
#     form = AddressCheckoutForm(request.POST or None)
#     next_ = request.GET.get('next')
#     next_post = request.POST.get('next')
#     redirect_path = next_ or next_post or None

#     print(form.errors)
#     print(request.POST.get('delivery_date'))

#     if form.is_valid():
#         print(request.POST)
#         instance = form.save(commit=False)

#         billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
#         if billing_profile is not None:
#             address_type = request.POST.get('address_type', 'shipping')
#             instance.billing_profile = billing_profile
#             instance.address_type = address_type
#             instance.save()

#             request.session[address_type + "_address_id"] = instance.id
#             billing_address_id = request.session.get("billing_address_id", None)
#             shipping_address_id = request.session.get("shipping_address_id", None)
#             city = request.session.get("city", None)

#             # Set delivery date to cart to pass through to order
#             cart_obj = Cart.objects.get(cart_session_id=request.session.session_key)
#             cart_obj.delivery_date = request.POST.get('delivery_date')
#             cart_obj.save()

#             # When user selects the check box "billing same as shipping"
#             # we automatically create the billing profile from the same information
#             # provided for the shipping address
#             if request.POST.get('billing_same_as_shipping') == "on":
#                 address_type = 'billing'
#                 instance.billing_profile = billing_profile
#                 instance.address_type = address_type
#                 instance.save()

#                 request.session[address_type + "_address_id"] = instance.id
#                 billing_address_id = request.session.get("billing_address_id", None)
#                 shipping_address_id = request.session.get("shipping_address_id", None)
#                 city = request.session.get("city", None)
#         else:
#             print("Error, Address Not Saved")
#             return redirect("cart:checkout")

#         if is_safe_url(redirect_path, request.get_host()):
#             return redirect(redirect_path)

#     return redirect("cart:checkout")


# def checkout_address_reuse_view(request):
#     if request.user.is_authenticated:
#         context = {}
#         next_ = request.GET.get('next')
#         next_post = request.POST.get('next')
#         redirect_path = next_ or next_post or None

#         if request.method == "POST":
#             shipping_address = request.POST.get('shipping_address', None)
#             address_type = request.POST.get('address_type', 'shipping')
#             billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)

#             if shipping_address is not None:
#                 qs = Address.objects.filter(billing_profile=billing_profile, id=shipping_address)
#                 if qs.exists():
#                     request.session[address_type + "_address_id"] = shipping_address
#                     cart_obj = Cart.objects.get(cart_session_id=request.session.session_key)
#                     cart_obj.delivery_date = request.POST.get('delivery_date')
#                 if is_safe_url(redirect_path, request.get_host()):
#                     return redirect(redirect_path)
#     return redirect("cart:checkout")
