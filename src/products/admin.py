from django.contrib import admin
from django.forms import Textarea
from django.db import models

from .models import *
from adminsortable2.admin import SortableAdminMixin

class ImageInLine(admin.TabularInline):
    model = ImageOption


class ColourOptionDetailInline(admin.TabularInline):
    model = ColourOption


class LengthOptionDetailInline(admin.TabularInline):
    model = LengthOption


class CategoryOptionDetailInline(admin.TabularInline):
    model = CategoryOption
    max_num = 5


class AccessoryOptionDetailInline(admin.TabularInline):
    model = AccessoryOption


class AdditionalDropDownOptionDetailInline(admin.TabularInline):
    model = AdditionalDropDownOption


class AdditionalDropDownAdmin(admin.ModelAdmin):
    class Meta:
        model = AdditionalDropDown


class ImageAdmin(admin.ModelAdmin):
	class Meta:
		model = Image


class ColourAdmin(admin.ModelAdmin):

    class Meta:
        model = Colour


class LengthAdmin(admin.ModelAdmin):

    class Meta:
        model = Length

    list_display = ('length', )


class CategoryAdmin(admin.ModelAdmin):

    class Meta:
        model = Category


class AccessoryAdmin(admin.ModelAdmin):

    class Meta:
        model = Accessory


class ProductAdmin(SortableAdminMixin, admin.ModelAdmin):

    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 3, 'cols': 40})}
    }

    fields = ('title', 'meta_title', 'meta_description', 'slug', 'description', 'more_info',
        'additional_dropdown_title',  
        'vic_title', 'nsw_title', 'qld_title', 'wa_title', 'vic_supplier_title', 'default_vic_supplier', 
        'nsw_supplier_title', 'default_nsw_supplier', 'qld_supplier_title', 'default_qld_supplier', 
        'wa_supplier_title', 'default_wa_supplier', 
        'vic_price', 'vic_price_per_mm', 'vic_supplier_per_mm', 'zincalume_discount_victoria',
        'nsw_price', 'nsw_price_per_mm', 'nsw_supplier_per_mm', 'zincalume_discount_new_south_wales',
        'qld_price', 'qld_price_per_mm', 'qld_supplier_per_mm', 'zincalume_discount_queensland',
        'wa_price', 'wa_price_per_mm', 'wa_supplier_per_mm', 'zincalume_discount_wa',
        'min_length', 'max_length', 'length_steps', 'youtube_embed_link', 'postage', 'packed', 'site', 'featured', 'active',
        'preload_colours', 'preload_lengths', 'preload_lengths_short_list')

    search_fields = ('title', 'nsw_title', 'qld_title', 'pk')

    list_filter = ('categoryoption__option',)

    list_display = ('title', 'category', 'vic_price', 'vic_price_per_mm', 'nsw_price', 'nsw_price_per_mm', 'qld_price', 'qld_price_per_mm', 'my_order',)

    def category(self, obj):
        try: 
            return str(obj.categoryoption_set.all().first().option)
        except AttributeError:
            return "No Category"

    def category_search(self, obj):
        try: 
            return str(obj.categoryoption_set.all().first().option)
        except AttributeError:
            return "No Category"

    class Meta:
        model = Product
        
    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js', # jquery
            'js/admin.js',   # app static folder
            'js/admin-product.js',
            )

    inlines = [ImageInLine, ColourOptionDetailInline, LengthOptionDetailInline,
               CategoryOptionDetailInline, AccessoryOptionDetailInline, AdditionalDropDownOptionDetailInline]




admin.site.register(Image, ImageAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Colour, ColourAdmin)
admin.site.register(Length, LengthAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Accessory, AccessoryAdmin)
admin.site.register(AdditionalDropDown, AdditionalDropDownAdmin)
