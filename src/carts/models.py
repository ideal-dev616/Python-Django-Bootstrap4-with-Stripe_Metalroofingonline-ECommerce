from decimal import Decimal
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_save, m2m_changed

from products.models import Product, Colour, Length, AdditionalDropDown

User = settings.AUTH_USER_MODEL
TWOPLACES = Decimal(10) ** -2

class CartManager(models.Manager):

    def new_or_get(self, request):
        cart_id = request.session.get("cart_id", None)
        qs = self.get_queryset().filter(id=cart_id)
        if qs.count() == 1:
            new_obj = False
            cart_obj = qs.first()
            if request.user.is_authenticated and cart_obj.user is None:
                cart_obj.user = request.user
                cart_obj.save()
        else:
            cart_obj = Cart.objects.new(user=request.user)
            new_obj = True
            request.session['cart_id'] = cart_obj.id
        return cart_obj, new_obj

    def new(self, user=None):
        user_obj = None
        if user is not None:
            if user.is_authenticated:
                user_obj = user
        return self.model.objects.create(user=user_obj)


class Cart(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT)
    cart_session_id = models.CharField(max_length=100, null=True, unique=True)
    total = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    delivery_date = models.CharField(max_length=120, blank=True, null=True)

    objects = CartManager()

    def __str__(self):
        return str(self.id)

    @property
    def is_digital(self):
        qs = self.products.all()  # every product
        new_qs = qs.filter(is_digital=False)  # every product that is not digial
        if new_qs.exists():
            return False
        return True
    
    def subtotal(self):
        subtotal = Decimal(self.total) / Decimal(1.1)
        return round(Decimal(subtotal), 2)

    def taxes(self):
        taxes = Decimal(self.total) / Decimal(11)
        return round(Decimal(taxes), 2)
    
    def calculateTotal(self):
        total = 0
        if len(self.cartitem_set.all()) > 0:
            for item in self.cartitem_set.all():
                total += item.price * item.quantity
        else:
            return 0
        
        return round(Decimal(total), 2)
    
    def save(self, *args, **kwargs):
        self.total = self.calculateTotal()
        super(Cart, self).save(*args, **kwargs)


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    colour = models.ForeignKey(Colour, null=True, blank=True, on_delete=models.SET_NULL)
    product_length = models.ForeignKey(Length, null=True, blank=True, on_delete=models.SET_NULL)
    additional_drop_down = models.ForeignKey(AdditionalDropDown, null=True, blank=True, on_delete=models.SET_NULL)
    length = models.DecimalField(default=0.00, max_digits=100, decimal_places=3, null=True, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=100, null=True, unique=True)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(default=0.00, max_digits=100, decimal_places=2, null=True, blank=True)
    line_price = models.DecimalField(default=0.00, max_digits=100, decimal_places=2, null=True, blank=True)

    def taxless_price(self):
        taxless = Decimal(self.price) / Decimal(1.1)
        return round(Decimal(taxless), 2)

    def taxless_line_price(self):
        taxless = Decimal(self.line_price) / Decimal(1.1)
        return round(Decimal(taxless), 2)

    def tax(self):
        tax = Decimal(self.price) / Decimal(11)
        return round(Decimal(tax), 2)


class CustomFlashing(models.Model):
    file = models.FileField(upload_to='pdf/')
    title = models.CharField(max_length=100, unique=True)
    
    
class CustomFlashingBelowMsg(models.Model):
    title = models.TextField(unique=True)