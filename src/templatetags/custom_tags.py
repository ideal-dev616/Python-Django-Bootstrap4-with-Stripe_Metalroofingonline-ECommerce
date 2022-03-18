from django import template
from django.conf import settings

from header_message.models import HeaderMessage
from home_page.models import Testimonial
from carts.models import Cart

register = template.Library()

@register.simple_tag
def get_setting(name):
    return getattr(settings, name, "")

@register.filter(name='addcss')
def addcss(field, css):
    attrs = {}
    definition = css.split(',')

    for d in definition:
        if ':' not in d:
            attrs['class'] = d
        else:
            t, v = d.split(':')
            attrs[t] = v

    return field.as_widget(attrs=attrs)

@register.inclusion_tag("message_list.html")
def get_header_message():
    headerMessages = HeaderMessage.objects.filter(active=True).order_by('id')
    if len(headerMessages) > 0:
        return {'message_list': [headerMessages[0]]}
    else:
        return {'message_list': []}

@register.inclusion_tag("message_list.html")
def get_header_message_checkout():
    headerMessages = HeaderMessage.objects.filter(active=True).order_by('id')
    if len(headerMessages) > 1:
        return {'message_list': [headerMessages[1]]}
    else:
        return {'message_list': []}

@register.inclusion_tag("testimonial.html")
def get_testimonials():
    return {'testimonials': Testimonial.objects.all()}

@register.inclusion_tag("get-cart.html", takes_context=True)
def get_cart(context):
    try:
        cart_obj = Cart.objects.filter(cart_session_id=context['request'].session.session_key).first()
    except:
        cart_obj = 0


    return { 'cart': Cart.objects.filter(cart_session_id=context['request'].session.session_key).first(), 
            'request': context['request']}
