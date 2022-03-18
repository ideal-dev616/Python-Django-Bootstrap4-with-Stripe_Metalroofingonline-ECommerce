from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.core.exceptions import MultipleObjectsReturned
from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404

from analytics.mixins import ObjectViewedMixin

from carts.models import Cart, CustomFlashing, CustomFlashingBelowMsg

from .models import Product

class ProductFeaturedListView(ListView):
    template_name = "products/list.html"

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.all().featured()

class ProductFeaturedDetailView(ObjectViewedMixin, DetailView):
    queryset = Product.objects.all().featured()
    template_name = "products/featured-detail.html"

    # def get_queryset(self, *args, **kwargs):
    #     request = self.request
    #     return Product.objects.featured()


class UserProductHistoryView(LoginRequiredMixin, ListView):
    template_name = "products/user-history.html"

    def get_context_data(self, *args, **kwargs):
        context = super(UserProductHistoryView, self).get_context_data(*args, **kwargs)
        try:
            cart_obj, cart_created = Cart.objects.get_or_create(cart_session_id=self.request.session.session_key)
        except MultipleObjectsReturned:
            cart_obj = Cart.objects.filter(cart_session_id=self.request.session.session_key).first()
        context['cart'] = cart_obj
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        views = request.user.objectviewed_set.by_model(
            Product, model_queryset=False)
        return views


class ProductListView(ListView):
    template_name = "products/list.html"

    # def get_context_data(self, *args, **kwargs):
    #     context = super(ProductListView, self).get_context_data(*args, **kwargs)
    #     print(context)
    #     return context

    def get_context_data(self, *args, **kwargs):
        context = super(ProductListView, self).get_context_data(
            *args, **kwargs)
        self.request.session.save()
        try:
            cart_obj, cart_created = Cart.objects.get_or_create(cart_session_id=self.request.session.session_key)
        except MultipleObjectsReturned:
            cart_obj = Cart.objects.filter(cart_session_id=self.request.session.session_key).first()
        context['cart'] = cart_obj
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.all()


def product_list_view(request):
    queryset = Product.objects.all()
    context = {
        'object_list': queryset
    }
    return render(request, "products/list.html", context)


class ProductDetailSlugView(ObjectViewedMixin, DetailView):
    queryset = Product.objects.all()
    template_name = "products/detail.html"

    def get_context_data(self, *args, **kwargs):
        state_selected = self.request.COOKIES.get('state')

        context = super(ProductDetailSlugView,
                        self).get_context_data(*args, **kwargs)

        try:
            cart_obj, cart_created = Cart.objects.get_or_create(cart_session_id=self.request.session.session_key)
        except MultipleObjectsReturned:
            cart_obj = Cart.objects.filter(cart_session_id=self.request.session.session_key).first()

        context['cart'] = cart_obj
        
        try:
            custom_flashings = [{'title': item.title, 'file': item.file} for item in CustomFlashing.objects.all()]
        except:
            custom_flashings = {}
            
        context['custom_flashings'] = custom_flashings
        
        try:
            custom_flashing_below_msgs = [{'title': item.title} for item in CustomFlashingBelowMsg.objects.all()]
        except:
            custom_flashing_below_msgs = {}
            
        context['custom_flashing_below_msgs'] = custom_flashing_below_msgs

        if state_selected == 'ACT':
            context['A_C_T'] = state_selected
        elif state_selected == 'NSW':
            context['NEW_SOUTH_WALES'] = state_selected
        elif state_selected == 'NT':
            context['NORTHERN_TERRITORY'] = state_selected
        elif state_selected == 'QLD':
            context['QUEENSLAND'] = state_selected
        elif state_selected == 'SA':
            context['SOUTH_AUSTRALIA'] = state_selected
        elif state_selected == 'TAS':
            context['TASMANIA'] = state_selected
        elif state_selected == 'VIC':
            context['VICTORIA'] = state_selected
        elif state_selected == 'WA':
            context['WESTERN_AUSTRALIA'] = state_selected

        return context

    def get_object(self, *args, **kwargs):
        request = self.request
        slug = self.kwargs.get('slug')

        # instance = get_object_or_404(Product, slug=slug, active=True)
        try:
            instance = Product.objects.get(slug=slug, active=True)
        except Product.DoesNotExist:
            raise Http404("Not found..")
        except Product.MultipleObjectsReturned:
            qs = Product.objects.filter(slug=slug, active=True)
            instance = qs.first()
        except:
            raise Http404("Uhhmmm ")
        return instance


class ProductDetailView(ObjectViewedMixin, DetailView):
    queryset = Product.objects.all()
    template_name = "products/detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailView, self).get_context_data(
            *args, **kwargs)
        print(context)
        # context['abc'] = 123
        return context

    def get_object(self, *args, **kwargs):
        request = self.request
        pk = self.kwargs.get('pk')
        instance = Product.objects.get_by_id(pk)
        if instance is None:
            raise Http404("Product doesn't exist")
        return instance

    # def get_queryset(self, *args, **kwargs):
    #     request = self.request
    #     pk = self.kwargs.get('pk')
    #     return Product.objects.filter(pk=pk)


def product_detail_view(request, pk=None, *args, **kwargs):
    instance = Product.objects.get_by_id(pk)

    if instance is None:
        raise Http404("Product doesn't exist")

    return render(request, "products/detail.html", context)
