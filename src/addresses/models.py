from django.db import models
from django.urls import reverse
from billing.models import BillingProfile


ADDRESS_TYPES = (
    ('billing', 'Billing address'),
    ('shipping', 'Shipping address'),
)

STATE_CHOICES = (
    ('victoria', 'VIC'),
    ('new south wales', 'NSW'),
    ('queensland', 'QLD'),
)


class Address(models.Model):
    first_name = models.CharField(max_length=120, default='')
    last_name = models.CharField(max_length=120, default='')
    phone_number = models.CharField(max_length=120, default='')
    address_type = models.CharField(max_length=120, choices=ADDRESS_TYPES, default='')
    address_line_1 = models.CharField(max_length=120, default='')
    address_line_2 = models.CharField(max_length=120, null=True, blank=True)
    city = models.CharField(max_length=120, default='')
    country = models.CharField(max_length=120, default='Australia')
    state = models.CharField(max_length=120, default='')
    postal_code = models.IntegerField(error_messages={'invalid':"Please Enter Australian Postal Code"}, default='0')

    def __str__(self):
        return str(self.address_line_1 + ", " + self.city + ", " + self.state)

    def get_absolute_url(self):
        return reverse("address-update", kwargs={"pk": self.pk})

    def get_short_address(self):
        return "{line1}, {city}".format(
            line1=self.address_line_1,
            city=self.city
        )

    def get_name(self):
        first_name = self.first_name
        last_name = self.last_name

        return "{first_name} {last_name}".format(
            first_name=first_name,
            last_name=last_name
        )

    def get_address(self):
        if self.address_line_2:
            return "{line1}\n{line2}\n{city}, \n{state}, \n{postal}, \n{country} \n{phone}".format(
            for_name=self.first_name or "",
            line1=self.address_line_1,
            line2=self.address_line_2 or "",
            city=self.city,
            state=self.state,
            postal=self.postal_code,
            country=self.country,
            phone=self.phone_number
        )

        return "{line1}, \n{city}, \n{state}, \n{postal}, \n{country} \n{phone}".format(
            for_name=self.first_name or "",
            line1=self.address_line_1,
            city=self.city,
            state=self.state,
            postal=self.postal_code,
            country=self.country,
            phone=self.phone_number,
        )

    def get_humanized_number(self):
        return ' '.join([str(self.phone_number)[i:i + 3] for i in range(1, len(str(self.phone_number)), 3)])
