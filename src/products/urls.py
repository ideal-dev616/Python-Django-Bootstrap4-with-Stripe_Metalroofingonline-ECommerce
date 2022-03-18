"""ecommerce URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, re_path

from .views import (
    ProductListView, 
    ProductDetailSlugView,
)

from categories.views import *

app_name = 'products'
urlpatterns = [
    path('', ProductListView.as_view(), name='list'),
    path('roofing-iron/', RoofingIronListView.as_view(), name='roofing-iron'),
    path('roofing-iron/colorbond', ColorbondListView.as_view(), name='colorbond'),
    path('roofing-iron/zincalume', ZincalumeListView.as_view(), name='zincalume'),
    # Guttering
    path('guttering/', GutteringListView.as_view(), name='guttering'),
    path('guttering/quad/', QuadListView.as_view(), name='quad'),
    path('guttering/sheerline/', SheerLineListView.as_view(), name='sheerline'),
    path('guttering/trimline/', TrimLineListView.as_view(), name='trimline'),
    path('guttering/half_round/', HalfRoundListView.as_view(), name='half_round'),

    # Rainwater Goods
    path('rainwater-goods/', RainwaterGoodsListView.as_view(), name='rainwater-goods'),
    
    path('rainwater-goods/fascia/', FasciaListView.as_view(), name='fascia'),
    path('rainwater-goods/downpipes/', DownpipesListView.as_view(), name='downpipes'),
    # Flashings
    path('flashings/', FlashingsListView.as_view(), name='flashings'),
    path('flashings/ridges/', RidgesListView.as_view(), name='ridges'),
    path('flashings/valleys/', ValleysListView.as_view(), name='valleys'),
    path('flashings/barge-cappings', BargeCappingsListView.as_view(), name='barge-cappings'),
    path('flashings/aprons', ApronsListView.as_view(), name='aprons'),
    path('flashings/box-gutters', BoxGuttersListView.as_view(), name='box-gutters'),
    path('flashings/flat-sheet', FlatSheetListView.as_view(), name='flat-sheet'),
    path('flashings/window-flashings', WindowFlashingsListView.as_view(), name='window-flashings'),
    # Polycarbonate
    path('polycarbonate/', PolycarbonateListView.as_view(), name='polycarbonate'),
    # Insulation
    path('insulation/', InsulationListView.as_view(), name='insulation'),
    # Accessories
    path('accessories/', AccessoriesListView.as_view(), name='accessories'),
    path('accessories/roofing-fasteners', RoofingFastenersListView.as_view(), name='roofing-fasteners'),
    path('accessories/gutter-guard', GutterGuardListView.as_view(), name='gutter-guard'),
    path('accessories/foam-strips', FoamStripsListView.as_view(), name='foam-strips'),
    path('accessories/roofing-tools', RoofingToolsListView.as_view(), name='roofing-tools'),
    path('accessories/downpipe-accessories', DownpipeAccessoriesListView.as_view(), name='downpipe-accessories'),
    path('accessories/fascia-accessories', FacsiaAccessoriesListView.as_view(), name='fascia-accessories'),
    path('accessories/adhesive-products', AdhesiveProductsListView.as_view(), name='adhesive-products'),
    re_path('(?P<slug>[\w-]+)/$', ProductDetailSlugView.as_view(), name='detail'),
]