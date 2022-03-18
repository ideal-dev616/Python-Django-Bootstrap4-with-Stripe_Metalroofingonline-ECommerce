from django.db import models

from tinymce import HTMLField

# Create your models here.
class YouTube(models.Model):
    title = models.CharField(max_length=120)
    embed = models.TextField()

    def __str__(self):
        return str(self.title)

class Testimonial(models.Model):
    testimonial = HTMLField('testimonial')

    def __str__(self):
        return str(self.pk)