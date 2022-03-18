from django.test import TestCase
from django.template.loader import render_to_string
from django.core.mail import send_mail

# Create your tests here.
def send_order_email(TestCase):

    msg_plain = render_to_string('../templates/email/order_confirmation.txt', {'order_obj': order_obj})
    msg_html = render_to_string('../templates/email/order_confirmation.html', {'order_obj': order_obj})

    subject = 'Order #' + order_obj.order_id + " confirmed."
    from_address = 'enquiries@metalroofingonline.com.au'
    recipient_list = 'ryanjohndunne@gmail.com'

    send_mail(subject, msg_plain, 'enquiries@metalroofingonline.com.au', ['ryanjohndunne@gmail.com'], html_message=msg_html)

    return