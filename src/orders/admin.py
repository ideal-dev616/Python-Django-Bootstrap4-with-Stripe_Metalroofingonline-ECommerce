import csv
from datetime import datetime
from collections import defaultdict

from django.contrib import admin
from django.http import HttpResponse
from django.urls import reverse, re_path, path
from django.utils.html import format_html
from django.shortcuts import render, redirect
from django.template.response import TemplateResponse

from ecommerce.utils import render_to_pdf
from shipping.models import State
from simple_history.admin import SimpleHistoryAdmin

from .models import Order, OrderItem


class OrderItemAdmin(admin.ModelAdmin):
    model = OrderItem


class OrderDetailInline(admin.TabularInline):
    model = OrderItem
    # raw_id_fields =  ('product', )
    extra = 1


class OrderAdmin(admin.ModelAdmin):
    list_per_page = 20
    'store', 'site', 'flash', 'pack', 'supplier_eta', 'customer_eta', 'tracking_number', 
    
    list_display = ('timestamp', 'order_id', 'name', 'delivery_date', 'suburb', 'total', 'status', 'email_status',
                    'account_actions')
    list_editable = ('status', 'email_status')

    history_list_display = ['status', 'total']
    inlines = [OrderDetailInline]
    search_fields = ('order_id', 'suburb', 'status', 'name', 'total')
    raw_id_fields = ('billing_profile', 'shipping_address', 'billing_address', 'cart')

    def get_queryset(self, request):
        query = super(OrderAdmin, self).get_queryset(request)
        filtered_query = query.filter(cart__isnull=True)
        return filtered_query

    def initiate_print_invoice(self, request, order_id, *args, **kwargs):
        return self.print_invoice(
            request=request,
            order_id=order_id,
        )

    def initiate_print_priceless_invoice(self, request, order_id, *args, **kwargs):
        return self.print_priceless_invoice(
            request=request,
            order_id=order_id,
        )

    def initiate_print_supplier(self, request, order_id, *args, **kwargs):
        return self.confirm_supplier(
            request=request,
            order_id=order_id,
        )

    def initiate_print_packing(self, request, order_id, *args, **kwargs):
        return self.confirm_packing(
            request=request,
            order_id=order_id,
        )

    def initiate_print_flashing(self, request, order_id, *args, **kwargs):
        return self.confirm_flashing(
            request=request,
            order_id=order_id,
        )

    def print_invoice(self, request, order_id):
        order = self.get_object(request, order_id)
        
        phone = order.shipping_address.phone_number
        phone = phone[:-6] + " " + phone[-6:-3] + " " + phone[-3:]
        order.shipping_address.phone_number = phone
        
        phone = order.billing_address.phone_number
        phone = phone[:-6] + " " + phone[-6:-3] + " " + phone[-3:]
        order.billing_address.phone_number = phone

        order.update_tax()
        
        context = {'order': order}

        pdf = render_to_pdf('pdf/invoice.html', context)
        return HttpResponse(pdf, content_type='application/pdf')

    def print_priceless_invoice(self, request, order_id):
        order = self.get_object(request, order_id)

        phone = order.shipping_address.phone_number
        phone = phone[:-6] + " " + phone[-6:-3] + " " + phone[-3:]
        order.shipping_address.phone_number = phone
        
        phone = order.billing_address.phone_number
        phone = phone[:-6] + " " + phone[-6:-3] + " " + phone[-3:]
        order.billing_address.phone_number = phone
        order.update_tax()
        
        context = {'order': order}

        pdf = render_to_pdf('pdf/invoice_no_prices.html', context)
        return HttpResponse(pdf, content_type='application/pdf')

    def confirm_supplier(self, request, order_id):
        order = self.get_object(request, order_id)
        lists = defaultdict(list)

        for item in order.orderitem_set.all():
            if item.destination == 'Store' or item.destination == 'Site':
                lists[item.product.name].append(item)

        if order.status == 'Created':
            order_paid = False
        else:
            order_paid = True

        lists = dict(lists)
        context = {
            'lists': lists,
            'order': order,
            'order_id': order_id,
            'type': 'supplier',
            'order_paid': order_paid,
        }

        return render(request, "pdf/confirm_pdf.html", context)

    def confirm_flashing(self, request, order_id):
        order = self.get_object(request, order_id)
        lists = defaultdict(list)

        for item in order.orderitem_set.all():
            for category in item.product.categoryoption_set.all():
                if str(category.option) == 'Flashings':
                    lists[item.product.name].append(item)
                    if str(order.shipping_address_final) == 'Pickup':
                        item.destination = 'Flashings'
                        item.save()

        if order.status == 'Created':
            order_paid = False
        else:
            order_paid = True

        lists = dict(lists)
        context = {
            'lists': lists,
            'order': order,
            'order_id': order_id,
            'type': 'flashing',
            'order_paid': order_paid,
        }

        return render(request, "pdf/confirm_pdf.html", context)

    def confirm_packing(self, request, order_id):
        order = self.get_object(request, order_id)
        lists = defaultdict(list)

        for item in order.orderitem_set.all():
            if item.destination == 'Stock':
                lists[item.product.name].append(item)

        if order.paid < order.total:
            order_paid = False
        else:
            order_paid = True

        lists = dict(lists)
        context = {
            'lists': lists,
            'order': order,
            'order_id': order_id,
            'type': 'supplier',
            'order_paid': order_paid,
        }

        return render(request, "pdf/confirm_pdf.html", context)

    def print_supplier(self, request, order_id):
        ''' Generate a pdf which contains all the items
        to be supplied by the default supplier and sent to site'''
        order = self.get_object(request, order_id)
        lists = defaultdict(list)

        order.supplier_total = 0

        for item in order.orderitem_set.all():
            if item.destination == 'Site' or item.destination == 'Store':
                item.ordered = True
                if not order.site:
                    order.site = 'Created'
                if item.to_be_picked:
                    item.to_be_picked = True
                item.save()

                order.supplier_total += item.line_price

        gst = float(order.supplier_total) * 0.10
        order.save()

        shippingState = 'VIC'
        if order.shipping_address.state == 'NSW' or order.shipping_address.state == 'ACT':
            shippingState = 'NSW'
        elif order.shipping_address.state == 'QLD':
            shippingState = 'QLD'
        elif order.shipping_address.state == 'WA':
            shippingState = 'WA'

        lists = dict(lists)
        context = {'order': order, 'order_id': order_id, 'gst': gst, 'shippingState': shippingState}

        pdf = render_to_pdf('pdf/supplier_invoice.html', context)
        return HttpResponse(pdf, content_type='application/pdf')

    def print_packing(self, request, order_id):
        '''
            Generate a pdf which contains all items to be picked by staff in-house.
            An item meets this requirement if product.packed is True and item.destination is 'Stock'
        '''

        order = self.get_object(request, order_id)
        lists = defaultdict(list)

        for item in order.orderitem_set.all():
            if item.destination == 'Stock' or 'Store' and item.product.packed:
                lists[item.product.name].append(item)
                item.to_be_picked = True
                if not order.pack:
                    order.pack = 'Created'
                item.save()

        order.save()

        lists = dict(lists)
        context = {'lists': lists, 'order': order, 'order_id': order_id}

        pdf = render_to_pdf('pdf/flashings.html', context)
        return HttpResponse(pdf, content_type='application/pdf')

    def print_flashing(self, request, order_id):
        ''' Generate a pdf which contains all the flashings to be made by the staff in-house '''
        order = self.get_object(request, order_id)
        lists = defaultdict(list)

        for item in order.orderitem_set.all():
            for category in item.product.categoryoption_set.all():
                if str(category.option) == 'Flashings':
                    lists[item.product.name].append(item)
                    item.ordered = True
                    if not order.flash:
                        order.flash = 'Created'
                    item.save()

        order.save()

        lists = dict(lists)
        context = {'lists': lists, 'order': order, 'order_id': order_id, }

        pdf = render_to_pdf('pdf/flashings.html', context)
        return HttpResponse(pdf, content_type='application/pdf')

    def initiate_email_customer(self, request, obj, order_id, *args, **kwargs):
        return self.email_customer(
            request=request,
            order_id=order_id
        )

    def email_customer(self, request, order_id):
        order = self.get_object(request, order_id)
        to_email = order.shipping_address.billing_profile.email

        subject = False
        message = False

        if order.email_status == 'Delivery ETA':
            # DELIVERY ETA
            subject = 'Your order #' + order.order_id + ' has been updated.'
            message = 'Thank you for choosing Metal Roofing Online for your roofing needs. \n'
            if order.tracking_number and order.customer_eta:
                message += 'Your order has been processed and estimated delivery date will be: ' + \
                           order.customer_eta + "\n" \
                           + 'Your accessories will arrive via Australia Post. Tracking ID: ' + \
                           order.tracking_number + "\n"
            elif order.tracking_number:
                message += 'Your accessories will arrive via Australia Post. Tracking ID: ' + \
                           order.tracking_number + "\n"
            elif order.tracking_number:
                message += 'Your order has been processed and estimated delivery date will be: ' + \
                           order.customer_eta + "\n"

            message += 'Please note: Delivery date accurate at time of notification, however may change with notice.'

        elif order.email_status == 'Changed Delivery Date':
            # CHANGED DELIVERY DATE
            subject = 'Your order #' + order.order_id + ' has changed delivery date.'

            message = 'Thank you for choosing Metal Roofing Online for your roofing needs. \n' \
                      + 'Your estimated delivery date has been updated and your order will now be estimated to arrive: '

            if order.customer_eta:
                message += order.customer_eta + '\n' \
                           + "Please note: Delivery date accurate at time of notification, however may change with notice."

        elif order.email_status == 'Posted':
            # POSTED
            message = "Thank you for choosing Metal Roofing Online. Your order has been posted and will arive via" \
                      + " Australia Post. Tracking ID: " + str(order.tracking_number)

        # TODO : Change from ryanjohndunne@gmail.com to metalroofing's
        # email
        from_email = 'ryanjohndunne@gmail.com'

        if not subject:
            subject = "NO SUBJECT CHOSEN"
        if not message:
            message = "NO MESSAGE CHOSEN"

        last_email = order.last_email

        context = {
            'subject': subject,
            'message': message,
            'from_email': from_email,
            'to_email': to_email,
            'order': order,
        }

        return render(request, "email/email_customer.html", context)

    def account_actions(self, obj):
        return format_html(
            '<a class="button" href="{}" target="_blank">Invoice</a>&nbsp;'
            '<a class="button" href="{}" target="_blank">Picking Slip</a>&nbsp;'
            '<a class="button" href="{}" target="_blank">Flashing</a>&nbsp;',
            reverse('admin:print-invoice', args=[obj.pk]),
            reverse('admin:print-priceless-invoice', args=[obj.pk]),
            reverse('admin:print-flashing', args=[obj.pk]),
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            re_path(
                r'(?P<order_id>.+)/invoice/',
                self.admin_site.admin_view(self.initiate_print_invoice),
                name='print-invoice',
            ),
            re_path(
                r'(?P<order_id>.+)/packing-slip/$',
                self.admin_site.admin_view(
                    self.initiate_print_priceless_invoice),
                name='print-priceless-invoice',
            ),
            re_path(
                r'(?P<order_id>.+)/confirm-supplier/$',
                self.admin_site.admin_view(self.initiate_print_supplier),
                name='confirm-supplier',
            ),
            re_path(
                r'(?P<order_id>.+)/print-supplier/$',
                self.admin_site.admin_view(self.print_supplier),
                name='print-supplier',
            ),
            re_path(
                r'(?P<order_id>.+)/confirm-flashing/$',
                self.admin_site.admin_view(self.initiate_print_flashing),
                name='confirm-flashing',
            ),
            re_path(
                r'(?P<order_id>.+)/print-flashing/$',
                self.admin_site.admin_view(self.print_flashing),
                name='print-flashing',
            ),
            re_path(
                r'(?P<order_id>.+)/confirm-packing/$',
                self.admin_site.admin_view(self.initiate_print_packing),
                name='confirm-packing',
            ),
            re_path(
                r'(?P<order_id>.+)/print-packing/$',
                self.admin_site.admin_view(self.print_packing),
                name='print-packing',
            ),
            re_path(
                r'(?P<order_id>.+)/email-customer/$',
                self.admin_site.admin_view(self.email_customer),
                name='email-customer',
            ),
        ]
        return custom_urls + urls

    def initiate_status_change(self, request, obj, status, *args, **kwargs):
        return redirect("admin/orders/order")

        if obj.status == 'Completed' and old_obj.status == 'Shipped':
            subject = 'Order #' + obj.order_id + " updated"
            message = 'Hello, ' + obj.shipping_address.first_name + \
                      ' thank you for shopping with metal roofing online!'
            from_address = 'enquiries@metalroofingonline.com.au'

            send_mail(subject, message, from_email, ['enquiries@metalroofingonline.com.au'])

    '''
        In-line elements are saved *after* the order and we need them *before* it is saved.
        These following three functions get the newly saved variables in the in lines
        so that we can determine the colour to display in the model view for statuses.

        Start: Inline Saving
    '''

    def response_add(self, request, new_object):
        obj = self.after_saving_model_and_related_inlines(new_object)
        return super(OrderAdmin, self).response_add(request, obj)

    def response_change(self, request, obj):
        obj = self.after_saving_model_and_related_inlines(obj)
        return super(OrderAdmin, self).response_change(request, obj)

    def after_saving_model_and_related_inlines(self, obj):
        return obj

    '''
        End: Inline Saving
    '''

    def save_model(self, request, obj, form, change):
        old_obj = self.model.objects.get(id=obj.id)
        dt = datetime.now().strftime("%d-%m-%Y %H:%M")

        obj = check_email_sent(obj, old_obj)
        obj.save()

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js',  # jquery
            'js/admin-order.js',  # app static folder
        )
        css = {
            'all': ('css/admin.css',)
        }

    account_actions.short_description = 'Invoice'
    account_actions.allow_tags = True


def check_email_sent(obj, old_obj):
    if obj.email_status != old_obj.email_status:
        obj.email_sent = False

    return obj


# Set displayed colours based on existance and progress of items in the order
def colour_setter(obj):
    store_error_check = False
    site_error_check = False
    flash_error_check = False
    pack_error_check = False

    store_exists = False
    site_exists = False
    flash_exists = False
    pack_exists = False

    for item in obj.orderitem_set.all():
        try:
            if item.product.categoryoption_set.all().first().option == 'Flashings':
                flash_exists = True
                if item.received and not item.packed or item.packed and not item.received:
                    flash = '?'
                    flash_error_check = True
                elif item.received and item.packed and not flash_error_check:
                    flash = '✓'
                else:
                    obj.flash = 'Created'
        except AttributeError:
            pass

        if item.destination == 'Store':
            store_exists = True
            if item.received and not item.packed or item.packed and not item.received:
                obj.store = '?'
                store_error_check = True
            elif item.received and item.packed and not store_error_check:
                obj.store = '✓'
            else:
                obj.store = 'Created'

        if item.destination == 'Site':
            site_exists = True
            obj.site = 'Created'
            if item.received and not item.packed or item.packed and not item.received:
                obj.site = '?'
                site_error_check = True
            elif item.received and item.packed and not site_error_check:
                obj.site = '✓'

        if item.destination == 'Pack':
            pack_exists = True
            if item.received and not item.packed or item.packed and not item.received:
                obj.pack = '?'
                pack_error_check = True
            elif item.received and item.packed and not pack_error_check:
                obj.pack = '✓'
            else:
                obj.pack = 'Created'

    if store_exists == False:
        obj.store = ' '

    if site_exists == False:
        obj.site = ' '

    if flash_exists == False:
        obj.flash = ' '

    if pack_exists == False:
        obj.pack = ' '

    return obj


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
