from django.db import models

STATE_CHOICES = (
    ('ALL', 'ALL'),
    ('ACT', 'ACT'),
    ('NSW', 'NSW'),
    ('NT', 'NT'),
    ('QLD', 'QLD'),
    ('TAS', 'TAS'),
    ('VIC', 'VIC'),
    ('WA', 'WA')
)

class Shipping(models.Model):
    title = models.CharField(max_length=120)

    def __str__(self):
        return self.title


class ShippingZone(models.Model):
    address = models.CharField(max_length=120)
    suburb = models.CharField(max_length=120)
    state = models.CharField(max_length=120)
    delivery_cost = models.DecimalField(
        null=True, blank=True, decimal_places=2, max_digits=20, default=0.00)
    max_distance = models.DecimalField(
        null=True, blank=True, decimal_places=2, max_digits=20, default=0.00, help_text="Maximum distance for zone's delivery in kilometres")
    
    def __str__(self):
        return self.address + ', ' + self.state


class ShippingOption(models.Model):
    shipping = models.ForeignKey(
        Shipping, on_delete=models.CASCADE, null=True, blank=True, max_length=120)
    option = models.ForeignKey(
        ShippingZone, on_delete=models.CASCADE, null=True, blank=True, max_length=120)


class Suburb(models.Model):
    postal_code = models.IntegerField(default=0)
    delivery_price = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    message = models.CharField(max_length=999, blank=True, null=True, help_text="If post code isn't shipped to entirely")

    def __str__(self):
        return str(self.postal_code)


class State(models.Model):
    title = models.CharField(max_length=120)
    approx_delivery_time = models.IntegerField(default=0, help_text="Approximate time in days")
    supplier = models.CharField(max_length=120)

    def __str__(self):
        return self.title

class DisallowedShippingDates(models.Model):
    date = models.DateField()
    state = models.CharField(max_length=120, choices=STATE_CHOICES, default='ALL')

    def __str__(self):
        return str(self.date)
