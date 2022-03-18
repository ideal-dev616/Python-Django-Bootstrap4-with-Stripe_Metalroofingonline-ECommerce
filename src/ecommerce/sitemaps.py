from django.contrib.sitemaps import Sitemap
from products.models import Product
from django.urls import reverse


class ProductSitemap(Sitemap):

    def items(self):
        return Product.objects.all()


class StaticViewSitemap(Sitemap):
    def items(self):
        return [
            'home',
            'about',
            'contact',
            'login',
            'register',
            'products:roofing-iron',
            'products:rainwater-goods',
            'products:guttering',
            'products:fascia',
            'products:downpipes',
            'products:flashings',
            'products:ridges',
            'products:valleys',
            'products:barge-cappings',
            'products:aprons',
            'products:box-gutters',
            'products:flat-sheet',
            'products:window-flashings',
            'products:polycarbonate',
            'products:insulation',
            'products:accessories',
            'products:roofing-fasteners',
            'products:gutter-guard',
            'products:foam-strips',
            'products:roofing-tools',
            'products:downpipe-accessories',
            'products:fascia-accessories',
            'products:adhesive-products',
            'products:list',
        ]

    def location(self, item):
        return reverse(item)
