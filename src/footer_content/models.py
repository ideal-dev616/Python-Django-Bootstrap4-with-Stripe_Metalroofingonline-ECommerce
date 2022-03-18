from django.db import models

from tinymce import HTMLField

class FooterContent(models.Model):
    page = models.CharField(max_length=120)
    meta_title = models.CharField(max_length=120, null=True, blank=True)
    meta_description = models.CharField(max_length=120, null=True, blank=True)
    content = HTMLField('Content')

    def __str__(self):
        return str(self.page)
