import math
import datetime

from django.core.mail import send_mail
from django.db import models
from django.db.models import Count, Sum, Avg
from django.db.models.signals import pre_save, post_save
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from addresses.models import Address
from billing.models import BillingProfile
from carts.models import Cart
from ecommerce.utils import unique_order_id_generator
from products.models import Product, Length, Colour, AdditionalDropDown
from simple_history.models import HistoricalRecords

from decimal import Decimal

TWOPLACES = Decimal(10) ** -2

EMAIL_STATUS_CHOICES = (
    ('Created', 'Created'),
    ('Paid', 'Paid'),
    ('Delivery ETA', 'Delivery ETA'),
    ('Changed Delivery Date', 'Changed Delivery Date'),
    ('Posted', 'Posted'),
    ('Collection Reminder', 'Collection Reminder'),
    ('VIC Collection', 'VIC Collection'),
    ('Pick Up ETA', 'Pick Up ETA'),
    ('Pick Up Date Change', 'Pick Up Date Change'),
)

ORDER_STATUS_CHOICES = (
    ('Created', 'Created'),
    ('Payment Accepted', 'Payment Accepted'),
    ('Reviewing Order', 'Reviewing Order'),
    ('In Progress', 'In Progress'),
    ('Scheduled', 'Scheduled'),
    ('Completed', 'Completed'),
    ('Refunded', 'Refunded'),
    ('Xero Invoice Awaiting Payment', 'Xero Invoice Awaiting Payment'),
    ('Waiting For Collection', 'Waiting For Collection'),
    ('Completed By Supplier', 'Completed By Supplier'),
    ('Completed', 'Completed'),
)

PROGRESS_STATUS_CHECK = (
    (' ', ' '),
    ('Created', 'Created'),
    ('Ordered', 'Ordered'),
    ('?', '?'),
    ('✓', '✓'),
)

DESTINATION_STATUS_CHECK = (
    ('Store', 'Store'),
    ('Site', 'Site'),
    ('Flashings', 'Flashings'),
    ('Stock', 'Stock'),
)

SUPPLIER_LIST = (
    (' ', ' '),
    ('Lysaght', 'Lysaght'),
    ('Ampelite', 'Ampelite'),
    ('MRO', 'MRO'),
    ('Metroll', 'Metroll'),
    ('Fletcher', 'Fletcher'),
    ('Battmans', 'Battmans'),
    ('Bremick', 'Bremick'),
)

ORDER_CODES = (
    (' ', ' '),
    ('VIC', 'VIC'),
    ('NSW', 'NSW'),
    ('QLD', 'QLD'),
    ('654', 'Delivery'),
    ('Postage', '427'),
    ('245', 'Standing Seam'),
    ('239', 'Inhouse Flashings')
)

SHIPPING_TYPES = (
    (' ', ' '),
    ('Standard Post', 'Standard Post'),
    ('Express Post', 'Express Post'),
    ('WA Standard Post', 'WA Standard Post'),
    ('WA Express Post', 'WA Express Post'),
    ('Pickup', 'Pickup'),
    ('VIC', 'VIC'),
    ('NSW', 'NSW'),
    ('QLD', 'QLD'),
    ('ACT', 'ACT'),
    ('TAS', 'TAS'),
    ('WA', 'WA'),
    ('NT', 'NT'),
)

PAYMENT_CHOICES = (
    ('Paypal', 'Paypal'),
    ('Stripe', 'Stripe'),
)


def shipping_check(order):
    POSTAGE = True
    for item in order.orderitem_set.all():
        if not item.packed:
            POSTAGE = False

    return POSTAGE


class OrderManagerQuerySet(models.query.QuerySet):

    def recent(self):
        return self.order_by("-updated", "-timestamp")

    def get_sales_breakdown(self):
        recent = self.recent().not_refunded()
        recent_data = recent.totals_data()
        recent_cart_data = recent.cart_data()
        shipped = recent.not_refunded().by_status(status='shipped')
        shipped_data = shipped.totals_data()
        paid = recent.by_status(status='paid')
        paid_data = paid.totals_data()
        data = {
            'recent': recent,
            'recent_data': recent_data,
            'recent_cart_data': recent_cart_data,
            'shipped': shipped,
            'shipped_data': shipped_data,
            'paid': paid,
            'paid_data': paid_data
        }
        return data

    def by_weeks_range(self, weeks_ago=7, number_of_weeks=2):
        if number_of_weeks > weeks_ago:
            number_of_weeks = weeks_ago
        days_ago_start = weeks_ago * 7  # days_ago_start = 49
        # days_ago_end = 49 - 14 = 35
        days_ago_end = days_ago_start - (number_of_weeks * 7)
        start_date = timezone.now() - datetime.timedelta(days=days_ago_start)
        end_date = timezone.now() - datetime.timedelta(days=days_ago_end)
        return self.by_range(start_date, end_date=end_date)

    def by_range(self, start_date, end_date=None):
        if end_date is None:
            return self.filter(updated__gte=start_date)
        return self.filter(updated__gte=start_date).filter(updated__lte=end_date)

    def by_date(self):
        now = timezone.now() - datetime.timedelta(days=9)
        return self.filter(updated__day__gte=now.day)

    def totals_data(self):
        return self.aggregate(Sum("total"), Avg("total"))

    def cart_data(self):
        return self.aggregate(
            Sum("cart__cartitem__product__price"),
            Avg("cart__cartitem__product__price"),
            Count("cart__cartitem__product")
        )

    def by_status(self, status="shipped"):
        return self.filter(status=status)

    def not_refunded(self):
        return self.exclude(status='refunded')

    def by_request(self, request):
        billing_profile, created = BillingProfile.objects.new_or_get(request)
        return self.filter(billing_profile=billing_profile)

    def not_created(self):
        return self.exclude(status='created')


class OrderManager(models.Manager):

    def get_queryset(self):
        return OrderManagerQuerySet(self.model, using=self._db)

    def by_request(self, request):
        return self.get_queryset().by_request(request)

    def new_or_get(self, billing_profile, cart_obj):
        created = False
        qs = self.get_queryset().filter(
            billing_profile=billing_profile,
            cart=cart_obj,
            active=True,
            status='created'
        )
        if qs.count() == 1:
            obj = qs.first()
        else:
            obj, created = self.model.objects.get_or_create(
                billing_profile=billing_profile,
                cart=cart_obj)
            obj.cart = cart_obj.id
            obj.save()
        return obj, created


# Random, Unique
class Order(models.Model):
    billing_profile = models.ForeignKey(
        BillingProfile, null=True, blank=True, on_delete=models.PROTECT)
    order_id = models.CharField(max_length=120, blank=True)
    tracking_number = models.CharField(max_length=99, blank=True, null=True)
    delivered = models.CharField(max_length=30, blank=True, null=True)
    shipping_address = models.ForeignKey(Address, related_name="shipping_address", null=True, blank=True,
                                         on_delete=models.PROTECT)
    billing_address = models.ForeignKey(Address, related_name="billing_address", null=True, blank=True,
                                        on_delete=models.PROTECT)
    shipping_address_final = models.TextField(blank=True, null=True)
    suburb = models.CharField(max_length=120, null=True, blank=True)
    billing_address_final = models.TextField(blank=True, null=True)
    name = models.CharField(max_length=120, blank=True, null=True, default="Anonymous")
    cart = models.ForeignKey(Cart, null=True, blank=True, on_delete=models.CASCADE)
    status = models.CharField(max_length=120, default='Created', choices=ORDER_STATUS_CHOICES)
    shipping_total = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    products_total = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    tax = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    total = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    paid = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    owed = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    supplier_total = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    flashings_total = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    packing_total = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    supplier_eta = models.CharField(max_length=11, blank=True, null=True)
    customer_eta = models.CharField(max_length=11, blank=True, null=True)
    store = models.CharField(max_length=120, default=' ', choices=PROGRESS_STATUS_CHECK)
    site = models.CharField(max_length=120, default=' ', choices=PROGRESS_STATUS_CHECK)
    flash = models.CharField(max_length=120, default=' ', choices=PROGRESS_STATUS_CHECK)
    pack = models.CharField(max_length=120, default=' ', choices=PROGRESS_STATUS_CHECK)
    notes = models.TextField(blank=True, null=True, default='Changes: \n')
    active = models.BooleanField(default=True)
    order_code = models.CharField(max_length=120, default=' ', choices=ORDER_CODES)
    shipping_type = models.CharField(max_length=120, default=' ', choices=SHIPPING_TYPES)
    last_email = models.TextField(max_length=999, default="No email has been sent to this customer yet.")
    email_status = models.CharField(max_length=120, default='Delivery ETA', choices=EMAIL_STATUS_CHOICES)
    email_sent = models.BooleanField(default=False)
    completion_image = models.ImageField(upload_to='', blank=True, null=True)
    payment_type = models.CharField(max_length=120, blank=True, null=True, choices=PAYMENT_CHOICES)
    delivery_date = models.CharField(max_length=120, blank=True, null=True)
    delivery_instructions = models.TextField(blank=True, null=True, default='')
    order_instructions = models.TextField(blank=True, null=True, default='')

    # history = HistoricalRecords()

    def __str__(self):
        return self.order_id

    objects = OrderManager()

    class Meta:
        ordering = ['-timestamp', '-updated']
        unique_together = ['cart']

    def subtotal(self):
        subtotal = (Decimal(self.total) - Decimal(self.shipping_total)) / Decimal(1.1)
        return round(subtotal, 2)

    def taxes(self):
        taxes = Decimal(self.total) / Decimal(11)
        return round(taxes, 2)

    def get_absolute_url(self):
        return reverse("orders:detail", kwargs={'order_id': self.order_id})

    def get_status(self):
        if self.status == "refunded":
            return "Refunded order"
        elif self.status == "shipped":
            return "Shipped"
        return "Shipping Soon"

    def get_owed(self):
        running_total = 0
        for item in self.orderitem_set.all():
            running_total += (item.price * item.quantity)
        new_total = round(Decimal(running_total) + Decimal(self.shipping_total), 2)
        self.total = round(new_total, 2)

        owed = new_total - self.owed

        return owed

    def get_total(self):
        running_total = 0
        for item in self.orderitem_set.all():
            running_total += (item.price * item.quantity)
        new_total = round(Decimal(running_total) + Decimal(self.shipping_total), 2)
        total = round(new_total, 2)

        return total

    def update_owed(self):
        owed = round(Decimal(self.total) - Decimal(self.paid), 2)
        self.owed = owed
        return self.owed

    def update_paid(self):
        paid = round(Decimal(self.total) - Decimal(self.owed), 2)
        self.paid = paid
        return self.paid

    def update_tax(self):
        # running_total = 0
        # for item in self.orderitem_set.all():
        #     running_total += item.price
        # tax = round(Decimal(running_total) / Decimal(11), 2)
        tax = round(Decimal(self.total) / Decimal(11), 2)
        print("UPDATE_TAX: " + str(tax))
        self.tax = round(tax, 2)
        return self.tax

    def update_total(self):
        running_total = 0
        for item in self.orderitem_set.all():
            running_total += (item.price * item.quantity)
        new_total = round(Decimal(running_total) + Decimal(self.shipping_total), 2)
        self.total = round(new_total, 2)

        return self.total

    def update_products_total(self):
        self.products_total = round(Decimal(self.total) - Decimal(self.shipping_total), 2)
        return self.products_total

    def check_done(self):
        shipping_done = False
        if self.shipping_address:
            shipping_done = True
        elif not self.shipping_address:
            shipping_done = False
        else:
            shipping_done = True
        billing_address = self.billing_address
        total = self.total
        if billing_address and shipping_done and total > 0:
            return True
        return False

    def update_purchases(self):
        for p in self.cart.cartitem_set.all():
            obj, created = ProductPurchase.objects.get_or_create(
                order_id=self.order_id,
                product=p.product,
                billing_profile=self.billing_profile
            )
        return ProductPurchase.objects.filter(order_id=self.order_id).count()

    def mark_paid(self):
        if self.status != 'paid':
            if self.check_done():
                self.status = "paid"
                self.save()
                self.update_purchases()
        return self.status


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    supplier = models.CharField(
        max_length=120, null=True, blank=True, choices=SUPPLIER_LIST)
    destination = models.CharField(
        max_length=120, null=True, blank=True, choices=DESTINATION_STATUS_CHECK)
    to_be_picked = models.BooleanField(default=False)
    ordered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    packed = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    order = models.ForeignKey(Order, null=True, blank=True, on_delete=models.CASCADE)
    colour = models.ForeignKey(Colour, null=True, blank=True, on_delete=models.PROTECT)
    product_length = models.ForeignKey(Length, null=True, blank=True, on_delete=models.SET_NULL)
    length = models.DecimalField(default=0.0000, max_digits=200, decimal_places=3, null=True, blank=True)
    additional_drop_down = models.ForeignKey(
        AdditionalDropDown, null=True, blank=True, on_delete=models.PROTECT)
    price = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    quantity = models.IntegerField(default=0)
    line_price = models.DecimalField(
        default=0.00, max_digits=100, decimal_places=2, null=True, blank=True)


########################################################################
#########                PRE SAVE METHODS HERE                ##########
########################################################################


def pre_save_create_order_id(sender, instance, *args, **kwargs):
    if not instance.order_id:
        instance.order_id = unique_order_id_generator(instance)
    qs = Order.objects.filter(cart=instance.cart).exclude(
        billing_profile=instance.billing_profile)
    if qs.exists():
        qs.update(active=False)

    if instance.shipping_address:
        if str(instance.shipping_address.address_line_1) == '48 Watt Rd' and str(
                instance.shipping_address.city) == 'Mornington':
            instance.shipping_address_final = 'Pickup'
            instance.suburb = 'Pickup'
            instance.name = instance.shipping_address.get_name()
        else:
            instance.shipping_address_final = instance.shipping_address.get_address()
            instance.name = instance.shipping_address.get_name()

    if instance.billing_address:
        if instance.shipping_address_final == 'Pickup':
            instance.billing_address_final = 'Pickup'
        else:
            instance.billing_address_final = instance.billing_address.get_address()
            instance.name = instance.billing_address.get_name()

    # Instance is being created
    if instance._state.adding:
        pass


pre_save.connect(pre_save_create_order_id, sender=Order)


def pre_save_set_shipping_type(sender, instance, *args, **kwargs):
    try:
        if instance.shipping_address.address_line_1 == '48 Watt Rd' and instance.shipping_address.city == 'Mornington':
            instance.shipping_type = 'Pickup'
        elif instance.shipping_address.state == 'VIC':
            if shipping_check(instance):
                instance.shipping_type = 'Postage'
            else:
                instance.shipping_type = 'VIC'
        elif instance.shipping_address.state == 'QLD':
            if shipping_check(instance):
                instance.shipping_type = 'Postage'
            else:
                instance.shipping_type = 'QLD'
        elif instance.shipping_address.state == 'NSW' or instance.shipping_address.state == 'ACT':
            if shipping_check(instance):
                instance.shipping_type = 'Postage'
            else:
                instance.shipping_type = 'NSW'
        elif instance.shipping_address.state == 'NT':
            instance.shipping_type = 'Postage'
        elif instance.shipping_address.state == 'TAS':
            instance.shipping_type = 'Postage'
        elif instance.shipping_address.state == 'WA':
            instance.shipping_type = 'Postage'
        elif instance.shipping_address.state == 'SA':
            instance.shipping_type = 'Postage'
    except AttributeError:
        pass


pre_save.connect(pre_save_set_shipping_type, sender=Order)


def pre_save_order(sender, instance, *args, **kwargs):
    print("PRE SAVE CALCULATE PRICES")
    instance.update_total()
    instance.update_tax()
    instance.update_products_total()
    instance.update_owed()
    instance.update_paid()


pre_save.connect(pre_save_order, sender=Order)


########################################################################
#########                POST SAVE METHODS HERE               ##########
########################################################################

def post_save_set_supplier_shipping(sender, instance, created, *args, **kwargs):
    # if not created:
    try:
        if instance.shipping_address.address_line_1 == '48 Watt Road' and instance.shipping_address.city == 'Mornington':
            instance.shipping_address_final = 'Pickup'
            instance.suburb = 'Pickup'
        else:
            instance.suburb = instance.shipping_address.city
    except AttributeError:
        pass


post_save.connect(post_save_set_supplier_shipping, sender=Order)


def post_save_email_in_progess(sender, instance, created, *args, **kwargs):
    print("POST SAVE EMAIL SENDING")

    if instance.status == 'In Progress':
        msg_plain = render_to_string('../templates/email/order_in_progress.txt', {'order_obj': instance})
        msg_html = render_to_string('../templates/email/order_in_progress.html', {'order_obj': instance})

        subject = "UPDATE: Your order is being processed!"
        from_address = 'enquiries@metalroofingonline.com.au'
        recipient_list = str(instance.billing_profile.email)

        send_mail(subject, msg_plain, 'enquiries@metalroofingonline.com.au', [str(instance.billing_profile.email)],
                  html_message=msg_html)

    return


post_save.connect(post_save_email_in_progess, sender=Order)


class ProductPurchaseQuerySet(models.query.QuerySet):

    def active(self):
        return self.filter(refunded=False)

    def digital(self):
        return self.filter(product__is_digital=True)

    def by_request(self, request):
        billing_profile, created = BillingProfile.objects.new_or_get(request)
        return self.filter(billing_profile=billing_profile)


class ProductPurchaseManager(models.Manager):

    def get_queryset(self):
        return ProductPurchaseQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset().active()

    def digital(self):
        return self.get_queryset().active().digital()

    def by_request(self, request):
        return self.get_queryset().by_request(request)

    def products_by_id(self, request):
        qs = self.by_request(request).digital()
        ids_ = [x.product.id for x in qs]
        return ids_

    def products_by_request(self, request):
        ids_ = self.products_by_id(request)
        products_qs = Product.objects.filter(id__in=ids_).distinct()
        return products_qs


class ProductPurchase(models.Model):
    order_id = models.CharField(max_length=120)
    # billingprofile.productpurchase_set.all()
    billing_profile = models.ForeignKey(
        BillingProfile, on_delete=models.CASCADE)
    # product.productpurchase_set.count()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    refunded = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ProductPurchaseManager()

    def __str__(self):
        return self.product.title
