from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin, actions

from .models import *


class ShippingDetailInLine(admin.TabularInline):
    model = ShippingOption


class ShippingZoneAdmin(admin.ModelAdmin):
	model = ShippingZone


class ShippingAdmin(admin.ModelAdmin):
    class Meta:
        model = Shipping

    inlines = [ShippingDetailInLine]

class SuburbAdmin(admin.ModelAdmin):
    class Meta:
        model = Suburb

    actions = ['set_price']

    def set_price(modeladmin, request, queryset):
        new_price = request.POST["new_price"]
        if new_price != "":
            queryset.update(delivery_price = new_price)
            messages.success(request, "Price(s) of selected record(s) has changed as {} successfully!".format(new_price))
        else:
            messages.warning(request, "Failed to change the price of the selected record.")

    list_display = ('postal_code', 'delivery_price')
    search_fields = ('postal_code',)

    # admin.site.add_action(set_price, "Set Price")

class DisallowedShippingDatesAdmin(admin.ModelAdmin):
    class Meta:
        model = DisallowedShippingDates
    
    def dateString(obj):
        return (str(obj.date))
    
    list_display = (dateString, 'state')


admin.site.register(Suburb, SuburbAdmin)
admin.site.register(DisallowedShippingDates, DisallowedShippingDatesAdmin)