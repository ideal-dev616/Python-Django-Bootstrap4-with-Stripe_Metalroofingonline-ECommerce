from django.contrib import admin

# Register your models here.
from .models import YouTube, Testimonial

admin.site.register(YouTube)
admin.site.register(Testimonial)