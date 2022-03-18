from django.urls import path, re_path
from django.views.generic import TemplateView

from .views import (
    OrderListView,
    OrderDetailView,
)

app_name = 'orders'
urlpatterns = [
    path('', OrderListView.as_view(), name='list'),
    re_path('(?P<order_id>[0-9][0-9][0-9]-[0-9][0-9][0-9]-[0-9][0-9][0-9]+)/', OrderDetailView.as_view(), name='detail'),
]
