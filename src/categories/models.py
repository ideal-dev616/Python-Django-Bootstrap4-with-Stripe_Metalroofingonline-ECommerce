from django.db import models

from tinymce import HTMLField

# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=100, null=True, unique=True)
    meta_title = models.CharField(max_length=70, help_text='Title for SEO', default="")
    meta_description = models.CharField(max_length=160, help_text='Description for SEO', default="")
    description = HTMLField('description')
    description_bottom = HTMLField('description_bottom')

    def __str__(self):
        return self.title