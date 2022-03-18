from django.shortcuts import render
from django.core.exceptions import MultipleObjectsReturned
from django.views.generic import ListView

from products.models import Product
from carts.models import Cart
from categories.models import Category


def get_common_context_data (me, context, title) :
    try:
        cart_obj, cart_created = Cart.objects.get_or_create(cart_session_id=me.request.session.session_key)
    except MultipleObjectsReturned:
        cart_obj = Cart.objects.filter(cart_session_id=me.request.session.session_key).first()

    try:
        category = Category.objects.filter(title=title).first()
        context['description'] = category.description
        context['description_bottom'] = category.description_bottom
        context['meta_title'] = category.meta_title
        context['meta_description'] = category.meta_description
    except:
        context['meta_title'] = ""
        context['meta_description'] = ""

    context['cart'] = cart_obj
    context['title'] = title

    

    return context
class RoofingIronListView(ListView):
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(RoofingIronListView, self).get_context_data(
            *args, **kwargs)
        self.request.session.save()
        
        return get_common_context_data(self, context, 'Roofing Iron')

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.filter(categoryoption__option__category='Roofing Iron')


class RainwaterGoodsListView(ListView):
    template_name = "products/list.html"


    def get_context_data(self, *args, **kwargs):
        context = super(RainwaterGoodsListView, self).get_context_data(
            *args, **kwargs)
        self.request.session.save()
        
        return get_common_context_data(self, context, 'Rainwater Goods')        

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.filter(categoryoption__option__category='Rainwater Goods')


class FlashingsListView(ListView):
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(FlashingsListView, self).get_context_data(
            *args, **kwargs)
        self.request.session.save()
        return get_common_context_data(self, context, 'Flashings')

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.filter(categoryoption__option__category='Flashings')


class PolycarbonateListView(ListView):
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(PolycarbonateListView, self).get_context_data(
            *args, **kwargs)
        self.request.session.save()
        return get_common_context_data(self, context, 'Polycarbonate')

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.filter(categoryoption__option__category='Polycarbonate')


class InsulationListView(ListView):
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(InsulationListView, self).get_context_data(
            *args, **kwargs)
        self.request.session.save()
        return get_common_context_data(self, context, 'Insulation')

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.filter(categoryoption__option__category='Insulation')


class AccessoriesListView(ListView):
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(AccessoriesListView, self).get_context_data(
            *args, **kwargs)
        self.request.session.save()
        return get_common_context_data(self, context, 'Accessories')

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.filter(categoryoption__option__category='Accessories')


class GutteringListView(ListView):
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(GutteringListView, self).get_context_data(
            *args, **kwargs)
        self.request.session.save()
        return get_common_context_data(self, context, 'Rainwater Goods - Guttering')

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.filter(categoryoption__option__category='Guttering')


class FasciaListView(ListView):
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(FasciaListView, self).get_context_data(
            *args, **kwargs)
        self.request.session.save()
        return get_common_context_data(self, context, 'Rainwater Goods - Fascia')

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.filter(categoryoption__option__category='Fascia')


class DownpipesListView(ListView):
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(DownpipesListView, self).get_context_data(
            *args, **kwargs)
        self.request.session.save()
        return get_common_context_data(self, context, 'Rainwater Goods - Downpipes')

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.filter(categoryoption__option__category='Downpipes')


class RidgesListView(ListView):
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(RidgesListView, self).get_context_data(
            *args, **kwargs)
        self.request.session.save()
        return get_common_context_data(self, context, 'Flashings - Ridges')

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.filter(categoryoption__option__category='Ridges')


class ValleysListView(ListView):
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ValleysListView, self).get_context_data(
            *args, **kwargs)
        self.request.session.save()
        return get_common_context_data(self, context, 'Flashings - Valleys')

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.filter(categoryoption__option__category='Valleys')


class BargeCappingsListView(ListView):
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(BargeCappingsListView, self).get_context_data(
            *args, **kwargs)
        self.request.session.save()
        return get_common_context_data(self, context, 'Flashings - Barge Cappings')

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.filter(categoryoption__option__category='Barge Capping')


class ApronsListView(ListView):
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ApronsListView, self).get_context_data(
            *args, **kwargs)
        self.request.session.save()
        return get_common_context_data(self, context, 'Flashings - Aprons')

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.filter(categoryoption__option__category='Apron Flashing')


class BoxGuttersListView(ListView):
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(BoxGuttersListView, self).get_context_data(
            *args, **kwargs)
        self.request.session.save()
        return get_common_context_data(self, context, 'Rainwater Goods - Box Gutters')

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.filter(categoryoption__option__category='Box Gutters')


class FlatSheetListView(ListView):
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(FlatSheetListView, self).get_context_data(
            *args, **kwargs)
        self.request.session.save()
        return get_common_context_data(self, context, 'Rainwater Goods - Flat Sheet')

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.filter(categoryoption__option__category='Flat Sheet')


class WindowFlashingsListView(ListView):
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(WindowFlashingsListView, self).get_context_data(
            *args, **kwargs)
        self.request.session.save()
        return get_common_context_data(self, context, 'Rainwater Goods - Window Flashings')

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.filter(categoryoption__option__category='Window Flashings')


class RoofingFastenersListView(ListView):
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(RoofingFastenersListView, self).get_context_data(
            *args, **kwargs)
        self.request.session.save()
        return get_common_context_data(self, context, 'Accessories - Rofing Fasteners')

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.filter(categoryoption__option__category='Roofing Fasteners')


class GutterGuardListView(ListView):
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(GutterGuardListView, self).get_context_data(
            *args, **kwargs)
        self.request.session.save()
        return get_common_context_data(self, context, 'Accessories - Gutter Guard')

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.filter(categoryoption__option__category='Gutter Guard')


class FoamStripsListView(ListView):
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(FoamStripsListView, self).get_context_data(
            *args, **kwargs)
        self.request.session.save()
        return get_common_context_data(self, context, 'Accessories - Foam Strips')

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.filter(categoryoption__option__category='Foam Strips')


class RoofingToolsListView(ListView):
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(RoofingToolsListView, self).get_context_data(
            *args, **kwargs)
        self.request.session.save()
        return get_common_context_data(self, context, 'Accessories - Roofing Tools')

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.filter(categoryoption__option__category='Roofing Tools')


class DownpipeAccessoriesListView(ListView):
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(DownpipeAccessoriesListView, self).get_context_data(
            *args, **kwargs)
        self.request.session.save()
        return get_common_context_data(self, context, 'Accessories - Downpipe Accessories')

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.filter(categoryoption__option__category='Downpipe Accessories')


class FacsiaAccessoriesListView(ListView):
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(FacsiaAccessoriesListView, self).get_context_data(
            *args, **kwargs)
        self.request.session.save()
        return get_common_context_data(self, context, 'Accessories - Fascia Accessories')

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.filter(categoryoption__option__category='Fascia Accessories')


class AdhesiveProductsListView(ListView):
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(AdhesiveProductsListView, self).get_context_data(
            *args, **kwargs)
        self.request.session.save()
        return get_common_context_data(self, context, 'Accessories - Adhesive Products')

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.filter(categoryoption__option__category='Adhesive Products')

class ColorbondListView(ListView):
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ColorbondListView, self).get_context_data(
            *args, **kwargs)
        self.request.session.save()
        return get_common_context_data(self, context, 'Roofing Iron - Colorbond')

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.filter(categoryoption__option__category='Colorbond')


class ZincalumeListView(ListView):
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ZincalumeListView, self).get_context_data(
            *args, **kwargs)
        self.request.session.save()
        return get_common_context_data(self, context, 'Roofing Iron - Zincalume')

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.filter(categoryoption__option__category='Zincalume')


class QuadListView(ListView):
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(QuadListView, self).get_context_data(
            *args, **kwargs)
        self.request.session.save()
        return get_common_context_data(self, context, 'Guttering - Quad')

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.filter(categoryoption__option__category='Quad')


class SheerLineListView(ListView):
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(SheerLineListView, self).get_context_data(
            *args, **kwargs)
        self.request.session.save()
        return get_common_context_data(self, context, 'Guttering - SheerLine')

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.filter(categoryoption__option__category='SheerLine')


class TrimLineListView(ListView):
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(TrimLineListView, self).get_context_data(
            *args, **kwargs)
        self.request.session.save()
        return get_common_context_data(self, context, 'Guttering - TrimLine')

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.filter(categoryoption__option__category='TrimLine')


class HalfRoundListView(ListView):
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(HalfRoundListView, self).get_context_data(
            *args, **kwargs)
        self.request.session.save()
        return get_common_context_data(self, context, 'Guttering - HalfRound')

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.filter(categoryoption__option__category='HalfRound')                                