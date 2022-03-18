from django.urls import path, re_path
from products.views import UserProductHistoryView
from accounts.views import (
    AccountHomeView,
    AccountEmailActivateView,
    UserDetailUpdateView,
)


app_name = 'accounts'
urlpatterns = [
    path('', AccountHomeView.as_view(), name='home'),
    path('details/', UserDetailUpdateView.as_view(), name='user-update'),
    path('history/products/', UserProductHistoryView.as_view(), name='user-product-history'),
    re_path('email/confirm/(?P<key>[0-9][0-9][0-9]-[0-9][0-9][0-9]-[0-9][0-9][0-9]+)/',
            AccountEmailActivateView.as_view(), name='email-activate'),
    re_path('email/resend-activation/',
            AccountEmailActivateView.as_view(), name='resend-activation'),
]