from django.conf import settings

from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.views.generic import UpdateView, View
from django.shortcuts import redirect

from .forms import MarketingPreferenceForm
from .mixins import CsrfExemptMixin
from .models import MarketingPreference
from .utils import Mailchimp

MAILCHIMP_EMAIL_LIST_ID = getattr(settings, "MAILCHIMP_EMAIL_LIST_ID", None)


class MarketingPreferenceUpdateView(SuccessMessageMixin, UpdateView):
    form_class = MarketingPreferenceForm
    template_name = 'base/forms.html'  # yeah create this
    success_url = '/settings/email/'
    success_message = 'Your email preferences have been updated. Thank you.'

    def dispatch(self, *args, **kwargs):
        user = self.request.user
        if not user.is_authenticated:
            # HttpResponse("Not allowed", status=400)
            return redirect("/login/?next=/settings/email/")
        return super(MarketingPreferenceUpdateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(MarketingPreferenceUpdateView,
                        self).get_context_data(*args, **kwargs)
        context['title'] = 'Update Email Preferences'
        return context

    def get_object(self):
        user = self.request.user
        obj, created = MarketingPreference.objects.get_or_create(
            user=user)  # get_absolute_url
        return obj


"""
POST METHOD
data[email]: emai@freddiesjokes.com
data[id]: 199a756cce
fired_at: 2018-02-12 04:30:26
data[merges][LNAME]:
data[merges][BIRTHDAY]:
type: subscribe
data[web_id]: 38951427
data[merges][EMAIL]: emai@freddiesjokes.com
data[merges][FNAME]:
data[list_id]: 71dd10f5fc
data[ip_opt]: 60.224.9.167
data[email_type]: html
"""


class MailchimpWebhookView(CsrfExemptMixin, View):

    def post(self, request, *args, **kwargs):
        data = request.POST
        list_id = data.get('data[list_id]')
        if str(list_id) == str(MAILCHIMP_EMAIL_LIST_ID):
            email = data.get('data[email]')
            hook_type = data.get('type')
            response_status, response = Mailchimp().check_subcription_status(email)
            sub_status = response['status']
            is_subbed = None
            mailchimp_subbed = None

            if sub_status == "subscribed":
                is_subbed, mailchimp_subbed = (True, True)
            elif sub_status == "unsubscribed":
                is_subbed, mailchimp_subbed = (False, False)
            if is_subbed is not None and mailchimp_subbed is not None:
                qs = MarketingPreference.objects.filter(
                    user__email__iexact=email)
                if qs.exists():
                    qs.update(subscribed=mailchimp_subbed,
                              mailchimp_subscribed=mailchimp_subbed, mailchimp_msg=str(data))

        return HttpResponse("Thank you", status=200)


# def mailchimp_webhook_view(request):
#     data = request.POST
#     list_id = data.get('data[list_id]')
#     if str(list_id) == str(MAILCHIMP_EMAIL_LIST_ID):
#         email = data.get('data[email]')
#         hook_type = data.get('type')
#         response_status, response = Mailchimp().check_subcription_status(email)
#         sub_status = response['status']
#         is_subbed = None
#         mailchimp_subbed = None

#         if sub_status == "subscribed":
#             is_subbed, mailchimp_subbed = (True, True)
#         elif sub_status == "unsubscribed":
#             is_subbed, mailchimp_subbed = (False, False)
#         if is_subbed is not None and mailchimp_subbed is not None:
#             qs = MarketingPreference.objects.filter(user__email__iexact=email)
#             if qs.exists():
#                 qs.update(subscribed=mailchimp_subbed,
#                           mailchimp_subscribed=mailchimp_subbed, mailchimp_msg=str(data))

#     return HttpResponse("Thank you", status=200)
