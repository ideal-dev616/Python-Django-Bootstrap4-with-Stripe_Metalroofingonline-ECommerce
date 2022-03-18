from django.contrib import admin

from .models import Address

class AddressAdmin(admin.ModelAdmin):
    list_display = ('address_line_1', 'phone_number')
    search_fields = ('address_line_1', 'phone_number', 'first_name', 'last_name')


admin.site.register(Address, AddressAdmin)
