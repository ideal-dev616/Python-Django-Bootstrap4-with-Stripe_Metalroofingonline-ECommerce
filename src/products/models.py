from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save, post_save
from django.urls import reverse

from tinymce import HTMLField
from random import randint
import re
import os

from ecommerce.utils import unique_slug_generator

SUPPLIER_LIST = (
    ('Supplier', 'Supplier'),
    ('Lysaght', 'Lysaght'),
    ('Ampelite', 'Ampelite'),
    ('MRO', 'MRO'),
    ('Metroll', 'Metroll'),
    ('Fletcher', 'Fletcher'),
    ('Battmans', 'Battmans'),
    ('Bremick', 'Bremick'),
)


def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_image_path(instance, filename):
    print(instance)
    print(filename)
    new_filename = randint(1, 3910209312)
    name, ext = get_filename_ext(filename)
    final_filename = '{new_filename}{ext}'.format(
        new_filename=new_filename, ext=ext)

    return "products/{new_filename}/{final_filename}".format(
        new_filename=new_filename,
        final_filename=final_filename
    )


class ProductQuerySet(models.query.QuerySet):

    def active(self):
        return self.filter(active=True)

    def featured(self):
        return self.filter(featured=True, active=True)

    def search(self, query):
        lookups = (Q(title__icontains=query) |
                   Q(description__icontains=query) |
                   Q(tag__title__icontains=query) |
                   Q(categoryoption__option__category__icontains=query)
                   )
        # Q(tag___name__icontains=query)
        return self.filter(lookups).distinct()


class ProductManager(models.Manager):

    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset().active()

    def featured(self):
        return self.get_queryset().featured()

    def get_by_id(self, id):
        qs = self.get_queryset().filter(id=id)  # Products.objects
        if qs.count() == 1:
            return qs.first()
        return None

    def search(self, query):
        return self.get_queryset().active().search(query)


class Product(models.Model):
    meta_title = models.CharField(
        max_length=70, help_text='Title for SEO')
    meta_description = models.CharField(
        max_length=160, help_text='Description for SEO')
    title = models.CharField(default='DEFAULT', max_length=120,
                             help_text='Generic name to display in backend')
    vic_title = models.CharField(max_length=120, null=True, blank=True)
    nsw_title = models.CharField(max_length=120, null=True, blank=True)
    qld_title = models.CharField(max_length=120, null=True, blank=True)
    vic_supplier_title = models.CharField(
        max_length=120, null=True, blank=True)
    nsw_supplier_title = models.CharField(
        max_length=120, null=True, blank=True)
    qld_supplier_title = models.CharField(
        max_length=120, null=True, blank=True)
    default_vic_supplier = models.CharField(
        max_length=120, null=True, blank=True,  default='Supplier', choices=SUPPLIER_LIST)
    default_nsw_supplier = models.CharField(
        max_length=120, null=True, blank=True, default='Supplier', choices=SUPPLIER_LIST)
    default_qld_supplier = models.CharField(
        max_length=120,  null=True, blank=True, default='Supplier', choices=SUPPLIER_LIST)
    old_url_vic = models.CharField(max_length=120, null=True, blank=True)
    old_url_nsw = models.CharField(max_length=120, null=True, blank=True)
    old_url_qld = models.CharField(max_length=120, null=True, blank=True)
    slug = models.SlugField(blank=True, unique=True, max_length=255)
    additional_dropdown_title = models.CharField(
        null=True, blank=True, max_length=120)
    description = HTMLField('Description')
    more_info = HTMLField('More Info')
    vic_price = models.DecimalField(
        decimal_places=2, max_digits=20, default=0.00)
    zincalume_discount_victoria = models.DecimalField(
        decimal_places=4, max_digits=20, default=0.0000)
    nsw_price = models.DecimalField(
        decimal_places=2, max_digits=20, default=0.00)
    zincalume_discount_new_south_wales = models.DecimalField(
        decimal_places=4, max_digits=20, default=0.0000)
    qld_price = models.DecimalField(
        decimal_places=2, max_digits=20, default=0.00)
    zincalume_discount_queensland = models.DecimalField(
        decimal_places=4, max_digits=20, default=0.0000)
    vic_price_per_mm = models.DecimalField(
        decimal_places=4, max_digits=20, default=0.000, null=True, blank=True)
    nsw_price_per_mm = models.DecimalField(
        decimal_places=4, max_digits=20, default=0.000, null=True, blank=True)
    qld_price_per_mm = models.DecimalField(
        decimal_places=4, max_digits=20, default=0.000, null=True, blank=True)
    vic_supplier_per_mm = models.DecimalField(
        decimal_places=4, max_digits=20, default=0.000, null=True, blank=True)
    nsw_supplier_per_mm = models.DecimalField(
        decimal_places=4, max_digits=20, default=0.000, null=True, blank=True)
    qld_supplier_per_mm = models.DecimalField(
        decimal_places=4, max_digits=20, default=0.000, null=True, blank=True)
    min_length = models.DecimalField(
        decimal_places=4, max_digits=20, default=0.0000, null=True, blank=True, help_text="Minimum length in mm")
    max_length = models.DecimalField(
        decimal_places=4, max_digits=20, default=0.0000, null=True, blank=True, help_text="Maximum length in mm")
    length_steps = models.DecimalField(decimal_places=4, max_digits=20, default=1.000, null=True, blank=True, help_text="Amount between lengths")
    youtube_embed_link = models.TextField(null=True, blank=True)
    postage = models.BooleanField(
        default=False, help_text="Sent via postage when order only contains postage items")
    packed = models.BooleanField(default=False, help_text="Packed in-house")
    site = models.BooleanField(
        default=False, help_text="Sent to site by supplier")
    featured = models.BooleanField(
        default=False, help_text='Displayed in the "featured" sections')
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    my_order = models.PositiveIntegerField(default=0, blank=False, null=False)
    preload_colours = models.BooleanField(
        default=False, help_text='Add all colours to product')
    preload_lengths = models.BooleanField(
        default=False, help_text='Add all lengths to product')
    preload_lengths_short_list = models.BooleanField(
        default=False, help_text="Add the shorter list of lengths")
    wa_title = models.CharField(max_length=120, null=True, blank=True)
    wa_supplier_title = models.CharField(max_length=120, null=True, blank=True)
    default_wa_supplier = models.CharField(max_length=120, null=True, blank=True,  default='Supplier', choices=SUPPLIER_LIST)
    wa_price = models.DecimalField(decimal_places=2, max_digits=20, default=0.00, null=True, blank=True)
    wa_price_per_mm = models.DecimalField(decimal_places=4, max_digits=20, default=0.000, null=True, blank=True)
    zincalume_discount_wa = models.DecimalField(decimal_places=4, max_digits=20, default=0.0000, null=True, blank=True)
    wa_supplier_per_mm = models.DecimalField(decimal_places=4, max_digits=20, default=0.000, null=True, blank=True)

    objects = ProductManager()

    def get_absolute_url(self):
        # return "/products/{slug}/".format(slug=self.slug)
        return reverse("products:detail", kwargs={"slug": self.slug})

    def price_without_tax(self):
        tax_price = float(self.price) * 0.90
        return "{0:.2f}".format(tax_price)

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title

    @property
    def name(self):
        return self.title

    class Meta:
        ordering = ['my_order']

    def stripped_title(self):
        title = self.title
        title = title.replace('COLOURBOND', '')
        title = title.replace('COLORBOND', '')
        title = title.replace('PLAIN', '')
        title = title.replace('ZINCALUME', '')
        title = title.replace('®', '')
        title = re.sub(r'\bor\b', '', title)

        return title



def post_save_set_colours(sender, instance, created, *args, **kwargs):

    try:
        unwanted_objects = [
            Colour.objects.get(colour='SIGN WHITE®'),
            Colour.objects.get(colour='MATT® MONUMENT®'),
            Colour.objects.get(colour='N/A'),
            Colour.objects.get(colour='NO COLOURS')
        ]

        colours = Colour.objects.all().exclude(
            id__in=[o.id for o in unwanted_objects])
    except:
        colours = Colour.objects.all()
        pass

    if instance.lengthoption_set.count() < 1 and instance.preload_lengths_short_list:

        lengths = Length.objects.filter(length__in=[1, 1.50, 2, 2.50, 3, 3.50, 4, 4.50, 5, 5.50, 6, 6.50, 7, 7.50, 8, 8.50, 9, 9.50, 10])

        for item in lengths:
            lengthoption = LengthOption(product=instance, option=item)
            lengthoption.save()

            instance.lengthoption_set.add(lengthoption)

    else:
        lengths = Length.objects.all().order_by('length')
        colours = colours.order_by('colour')

        if instance.colouroption_set.count() < 1 and instance.preload_colours:
            for item in colours:
                colouroption = ColourOption(product=instance, option=item)
                colouroption.save()

                instance.colouroption_set.add(colouroption)

        if instance.lengthoption_set.count() < 1 and instance.preload_lengths:
            for item in lengths:
                lengthoption = LengthOption(product=instance, option=item)
                lengthoption.save()

                instance.lengthoption_set.add(lengthoption)


post_save.connect(post_save_set_colours, sender=Product)


class Colour(models.Model):
    colour = models.CharField(null=True, blank=True, max_length=120)
    hex_value = models.CharField(null=True, blank=True, max_length=120, help_text="Hex value for colour e.g:  #ff5733")
    additional_cost = models.DecimalField(
        null=True, blank=True, decimal_places=2, max_digits=20, default=0.00)

    def __str__(self):
        return self.colour

    @property
    def name(self):
        return self.colour


class Length(models.Model):
    length = models.DecimalField(null=True, blank=True, decimal_places=3,
                                 max_digits=20, default=0.000, help_text="Length in metres")

    def __str__(self):
        return str(self.length)

    @property
    def name(self):
        return str(self.length)

    def length_converted(self):
        length = int(self.length * 1000)
        return str(length)

    class Meta:
        ordering = ['length']


class Category(models.Model):
    category = models.CharField(null=True, blank=True, max_length=120)

    def __str__(self):
        return self.category

    @property
    def name(self):
        return self.category


class Accessory(models.Model):
    accessory = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=True, blank=True, max_length=120)

    def __str__(self):
        return self.accessory.title

    @property
    def name(self):
        return self.accessory.title


class Image(models.Model):
    image = models.ImageField(upload_to=upload_image_path)
    title = models.CharField(max_length=120)
    alt = models.CharField(max_length=120)

    def __str__(self):
        return self.title

    @property
    def name(self):
        return self.title


class AdditionalDropDown(models.Model):
    title = models.CharField(max_length=120)
    additional_cost = models.DecimalField(
        null=True, blank=True, decimal_places=2, max_digits=20, default=0.00)
    zincalume_discount = models.DecimalField(
        null=True, blank=True, decimal_places=2, max_digits=20, default=0.00)

    def __str__(self):
        return self.title

    @property
    def name(self):
        return self.title


class AdditionalDropDownOption(models.Model):
    product = models.ForeignKey(
        Product, null=True, blank=True, on_delete=models.CASCADE)
    option = models.ForeignKey(
        AdditionalDropDown, null=True, blank=True, on_delete=models.CASCADE)


class ImageOption(models.Model):
    product = models.ForeignKey(
        Product, null=True, blank=True, on_delete=models.CASCADE)
    option = models.ForeignKey(
        Image, null=True, blank=True, on_delete=models.CASCADE)


class ColourOption(models.Model):
    # Access chosen colours with - product.colouroption_set.all()
    product = models.ForeignKey(
        Product, null=True, blank=True, on_delete=models.CASCADE)
    option = models.ForeignKey(Colour, null=True, blank=True,
                               on_delete=models.CASCADE, help_text="Length in Metres")

    def cleaned_option(self):
        option = str(self.option)
        cleaned = re.sub(r'[?|@|.|!|(|)|$| |®]', r'', option)

        return cleaned


class LengthOption(models.Model):
    # Access chosen lengths with - product.lengthoption_set.all()
    product = models.ForeignKey(
        Product, null=True, blank=True, on_delete=models.CASCADE)
    option = models.ForeignKey(
        Length, null=True, blank=True, on_delete=models.CASCADE)


class CategoryOption(models.Model):
    # Access chosen colours with - product.colouroption_set.all()
    product = models.ForeignKey(
        Product, null=True, blank=True, on_delete=models.CASCADE)
    option = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.CASCADE)


class AccessoryOption(models.Model):
    # Access chosen accessories with - product.accessoryoption_set.all()
    product = models.ForeignKey(
        Product, null=True, blank=True, on_delete=models.CASCADE)
    option = models.ForeignKey(
        Accessory, null=True, blank=True, on_delete=models.CASCADE)


def product_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


pre_save.connect(product_pre_save_receiver, sender=Product)
