"""ecommerce URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include

from .views import (
    saved_cart,
    checkout_new,
    cart_home,
    cart_update,
    checkout_home,
    checkout_paypal,
    checkout_done_view,
    cart_changed_state,
    cart_clear,
    validate_form_stripe,
    validate_form_paypal,
    validate_form_cart,
)

from carts.api.addToCart import addToCart
from carts.api.removeFromCart import removeFromCart
from carts.api.convertNewLengths import convertNewLengths
from carts.api.removeCartsAndItems import removeCarts
from carts.api.setNewLengths import createNewMaxLength

app_name = 'cart'
urlpatterns = [
    path('', cart_home, name='home'),
    path('saved-cart/', saved_cart, name='saved_cart'),
    path('checkout/', checkout_new, name='checkout'),
    path('checkout_home/', checkout_home, name='checkout_home'),
    path('update/', cart_update, name='update'),
    path('addtocart/', addToCart, name='add'),
    path('removefromcart/', removeFromCart, name='remove'),
    path('checkout/success/', checkout_done_view, name='success'),
    path('checkout/paypal/', checkout_paypal, name='checkout-paypal'),
    path('validate-form-stripe/', validate_form_stripe, name='validate-form-stripe'),
    path('validate-form-paypal/', validate_form_paypal, name='validate-form-paypal'),
    path('validate-form-cart/', validate_form_cart, name='validate-form-cart'),
    path('convert-lengths/', convertNewLengths, name="convert-new-lengths"),
    path('remove-carts/', removeCarts, name="remove-carts"),
    #  path('new-lengths/', createNewMaxLength, name="remove-carts")
]
