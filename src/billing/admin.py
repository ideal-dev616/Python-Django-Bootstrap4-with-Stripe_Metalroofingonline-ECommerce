from django.contrib import admin

from.models import BillingProfile, Card, Charge

class BillingProfileAdmin(admin.ModelAdmin):
    model = BillingProfile
    search_fields = ('email',)

admin.site.register(BillingProfile,BillingProfileAdmin)

admin.site.register(Card)

admin.site.register(Charge)
