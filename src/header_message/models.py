from django.db import models

from tinymce import HTMLField

COLOUR_LIST = (
    ('Blue', 'Blue'),
    ('Grey', 'Grey'),
    ('Green', 'Green'),
    ('Red', 'Red'),
    ('Yellow', 'Yellow'),
    ('Teal', 'Teal'),
    ('Light Grey', 'Light Grey'),
    ('Dark Grey', 'Dark Grey'),
)

# Create your models here.
class HeaderMessage(models.Model):
    message = HTMLField('Message')
    active = models.BooleanField(default=True)
    colour = models.CharField(
        max_length=120, null=True, blank=True,  default='Blue', choices=COLOUR_LIST)

    def __str__(self):
        return str(self.message)