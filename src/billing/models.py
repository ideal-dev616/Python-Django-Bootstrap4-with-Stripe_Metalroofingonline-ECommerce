from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.shortcuts import render, redirect
from django.urls import reverse

from accounts.models import GuestEmail

from decimal import *
from datetime import datetime

from xero import Xero
from xero.auth import PrivateCredentials

import stripe

User = settings.AUTH_USER_MODEL
VERSION = getattr(settings, 'VERSION', 'PROD')
STRIPE_SECRET_KEY = getattr(settings, "STRIPE_SECRET_KEY", 'error')
STRIPE_PUB_KEY = getattr(settings, "STRIPE_PUB_KEY", 'error')
stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", 'error')
XERO_RSA_KEY = getattr(settings, "XERO_RSA_KEY", 'error')
XERO_SECRET_KEY = getattr(settings, 'XERO_SECRET_KEY', 'error')
# When rounding decimal to two places
TWOPLACES = Decimal(10) ** -2


class BillingProfileManager(models.Manager):

    def new_or_get(self, request):
        user = request.user
        guest_email_id = request.session.get('guest_email_id')
        created = False
        obj = None

        # Logic for user and guest checkout
        if user.is_authenticated:
            # Logged in user checkout; remember payment info
            obj, created = self.model.objects.get_or_create(
                user=user, email=user.email)
        elif guest_email_id is not None:
            # Guest user checkout; auto reload payment info
            guest_email_obj = GuestEmail.objects.get(id=guest_email_id)
            try:
                obj, created = self.model.objects.get_or_create(email=guest_email_obj.email)
            except:
                obj = self.model.objects.filter(email=guest_email_obj.email).first()
                created = False

        else:
            pass

        return obj, created


class BillingProfile(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.PROTECT)
    email = models.EmailField()
    active = models.BooleanField(default=True)
    update = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    customer_id = models.CharField(max_length=120, null=True, blank=True)

    objects = BillingProfileManager()

    def __str__(self):
        return self.email

    def charge(self, order_obj, card=None):
        return Charge.objects.do(self, order_obj, card)

    # Filtered list of all cards (doesn't include inactive cards)
    def get_cards(self):
        return self.card_set.all()

    def get_payment_method_url(self):
        return reverse('billing-payment-method')

    @property
    def has_card(self):  # instance.has_card
        card_qs = self.get_cards()
        return card_qs.exists()  # True or False

    @property
    def default_card(self):
        default_cards = self.get_cards().filter(active=True, default=True)
        if default_cards.exists():
            return default_cards.first()
        return None

    def set_cards_inactive(self):
        cards_qs = self.get_cards()
        cards_qs.update(active=False)
        return cards_qs.filter(active=True).count()


def billing_profile_created_receiver(sender, instance, *args, **kwargs):
    if not instance.customer_id and instance.email:
        print("ACTUAL API REQUEST send to stripe")
        customer = stripe.Customer.create(
            email=instance.email
        )
        print(customer)
        instance.customer_id = customer.id


pre_save.connect(billing_profile_created_receiver, sender=BillingProfile)


def user_created_receiver(sender, instance, created, *args, **kwargs):
    if created and instance.email:
        BillingProfile.objects.get_or_create(
            user=instance, email=instance.email)


post_save.connect(user_created_receiver, sender=User)


class CardManager(models.Manager):

    # Don't return cards that have been made inactive
    def all(self, *args, **kwargs):
        return self.get_queryset().filter(active=True)

    def add_new(self, billing_profile, token):
        if token:
            customer = stripe.Customer.retrieve(billing_profile.customer_id)
            print(customer)
            card_response = customer.sources.create(source=token)
            new_card = self.model(
                billing_profile=billing_profile,
                stripe_id=card_response.id,
                brand=card_response.brand,
                country=card_response.country,
                exp_month=card_response.exp_month,
                exp_year=card_response.exp_year,
                last4=card_response.last4
            )
            new_card.save()

            return new_card
        return None


class Card(models.Model):
    billing_profile = models.ForeignKey(BillingProfile, on_delete=models.PROTECT)
    stripe_id = models.CharField(max_length=120)
    brand = models.CharField(max_length=120, null=True, blank=True)
    country = models.CharField(max_length=20, null=True, blank=True)
    exp_month = models.IntegerField(null=True, blank=True)
    exp_year = models.IntegerField(null=True, blank=True)
    last4 = models.CharField(max_length=4, null=True, blank=True)
    default = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = CardManager()

    def __str__(self):
        return "{} {}".format(self.brand, self.last4)


# When user adds a new card we want to set it as the default
def new_card_post_save_receiver(sender, instance, created, *args, **kwargs):
    if instance.default:
        billing_profile = instance.billing_profile
        qs = Card.objects.filter(billing_profile=billing_profile).exclude(pk=instance.pk)
        qs.update(default=False)


post_save.connect(new_card_post_save_receiver, sender=Card)


class ChargeManager(models.Manager):

    def do(self, billing_profile, order_obj, card=None):  # Charge.objects.do()
        card_obj = card
        if card_obj is None:
            cards = billing_profile.card_set.filter(default=True)  # card_obj.billing_profile
            
            if cards.exists():
                card_obj = cards.first()
        
        if card_obj is None:
            return False, "No cards available"
        

        c = stripe.Charge.create(
            amount=int(order_obj.total * 100),  # 39.19 --> 3919
            currency="aud",
            customer=billing_profile.customer_id,
            source=card_obj.stripe_id,
            metadata={"order_id": order_obj.order_id},
        )
        new_charge_obj = self.model(
            billing_profile=billing_profile,
            stripe_id=c.id,
            paid=c.paid,
            refunded=c.refunded,
            outcome=c.outcome,
            outcome_type=c.outcome['type'],
            seller_message=c.outcome.get('seller_message'),
            risk_level=c.outcome.get('risk_level'),
        )
        new_charge_obj.save()

        # Create an invoice deducting stripe fee's
        # stripe_payment = stripe.BalanceTransaction.retrieve(c['balance_transaction'])
        # stripe_payment = Decimal(stripe_payment['fee']) / Decimal(100)
        # xero_stripe_fee(stripe_payment)

        return new_charge_obj.paid, new_charge_obj.seller_message


class Charge(models.Model):
    billing_profile = models.ForeignKey(BillingProfile, on_delete=models.CASCADE)
    stripe_id = models.CharField(max_length=120)
    paid = models.BooleanField(default=False)
    refunded = models.BooleanField(default=False)
    outcome = models.TextField(null=True, blank=True)
    outcome_type = models.CharField(max_length=120, null=True, blank=True)
    seller_message = models.CharField(max_length=120, null=True, blank=True)
    risk_level = models.CharField(max_length=120, null=True, blank=True)

    objects = ChargeManager()


def xero_stripe_fee(stripe_payment):
    with open(XERO_RSA_KEY) as keyfile:
        rsa_key = keyfile.read()
    credentials = PrivateCredentials(XERO_SECRET_KEY, rsa_key)
    xero = Xero(credentials)
    time = datetime.now()

    invoice = {
        "Type": "ACCPAY",
        "CurrencyCode": "AUD",
        "Contact": {"Name": "Stripe Fee"},
        "Date": datetime(time.year, time.month, time.day),
        "DueDate": datetime(time.year, time.month, time.day),
        "Total": str(stripe_payment),
        "LineItems": [
            {
                "Description": "Stripe Fee",
                "Quantity": "1.00",
                "UnitAmount": str(stripe_payment),
                "AccountCode": "407",
                "TaxType": "EXEMPTEXPENSES",
            }
        ],
        "Status": "AUTHORISED",
    }

    new_invoice = xero.invoices.put(invoice)

    # Add payment of stripe fee
    invoiceID = new_invoice[0]['InvoiceID']

    payment = {
        "Invoice": {"InvoiceID": invoiceID},
        "Account": {"Code": "STRIPE"},
        "Date": datetime(time.year, time.month, time.day, time.hour, time.minute),
        "Amount": str(stripe_payment),
    }

    new_payment = xero.payments.put(payment)

    return
