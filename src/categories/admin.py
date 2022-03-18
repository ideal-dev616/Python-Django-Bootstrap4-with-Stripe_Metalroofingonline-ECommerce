from django.contrib import admin
from django.forms import Textarea

from .models import *

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 3, 'cols': 40})}
    }

    class Meta:
        model = Category

admin.site.register(Category, CategoryAdmin)