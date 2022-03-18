from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import render
from django.urls import path, re_path, reverse

from .models import Cart, CartItem, CustomFlashing, CustomFlashingBelowMsg
from orders.models import Order

class CartItemAdmin(admin.ModelAdmin):
    model = CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem

# class OrderItemAdmin(admin.ModelAdmin):
#     model = Order

class OrderInline(admin.TabularInline):
    fields = ['order_id', 'billing_profile', 'shipping_address_final', 'suburb', 'billing_address_final', 'name', 'status']
    model = Order
    verbose_name = "Saved_Cart"
    verbose_name_plural = "Saved Cart"


class CartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'total', 'cart_session_id', 'cart_actions')
    inlines = [CartItemInline, OrderInline]
    search_fields = ('total', 'pk', 'cart_session_id')

    # def get_queryset(self, request):
    #     # query = Order.objects.select_related('cart')
    #     query = Cart.objects.filter(order__cart__isnull=False)
    #     # query = Cart.objects.select_related(order__cart)
    #     # Department.objects.filter(departmentvolunteer__department__isnull=True)

    #     # query = super(CartAdmin, self).get_queryset(request)
    #     filtered_query = query
    #     return filtered_query

    def initiate_xero_invoice(self, request, pk, *args, **kwargs):
        return self.create_xero_invoice(
            request=request,
            pk=pk,
        )

    def create_xero_invoice(self, request, pk):
        cart = self.get_object(request, pk)
        context = {'cart': cart}

        return render(request, "xero/contact-shipping.html", context)

    def cart_actions(self, obj):
        return format_html(
            '<a class="button" href="{}" target="_blank">Xero Invoice</a>&nbsp;',
            reverse('admin:xero-invoice', args=[obj.pk]),
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            re_path(
                r'(?P<pk>.+)/invoice/',
                self.admin_site.admin_view(self.initiate_xero_invoice),
                name='xero-invoice',
            ),
        ]
        return custom_urls + urls
    

class CustomFlashingsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'file')
    
class CustomFlashingBelowMsgAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title')


admin.site.register(Cart, CartAdmin)
admin.site.register(CustomFlashing, CustomFlashingsAdmin)
admin.site.register(CustomFlashingBelowMsg, CustomFlashingBelowMsgAdmin)
admin.site.register(CartItem, CartItemAdmin)
