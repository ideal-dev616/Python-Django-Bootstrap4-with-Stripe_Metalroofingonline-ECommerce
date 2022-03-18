from django.urls import path, re_path

from .views import (
    DeliveryView,
    TOSView,
    FAQView,
    RefundView,
    TechnicalView,
    MetalRoofingSheetsView,
    GutteringView,
    EavesGutteringView,
    InsulationBattsView,
    PolycarbonateRoofingView,
    FlashingView,
    MetalRoofInsulationView,
    WarrantyView,
    ColourbondColoursView
)

app_name = 'footer_content'
urlpatterns = [
    path('delivery/', DeliveryView, name='delivery'),
    path('TOS/', TOSView, name='TOS'),
    path('FAQ/', FAQView, name='FAQ'),
    path('refund-policy/', RefundView, name='refund'),
    path('technical-centre/', TechnicalView, name='technical'),
    path('warranty/', WarrantyView, name='warranty'),
    path('colourbond-colours/', ColourbondColoursView, name='colourbond-colours'),


    path('hti-metalroofingsheets/', MetalRoofingSheetsView, name='hti-metalroofingsheets'),
    path('hti-guttering/', GutteringView, name='hti-guttering'),
    path('hti-eavesguttering/', EavesGutteringView, name='hti-eavesgutteringview'),
    path('hti-insulationbatts/', InsulationBattsView, name='hti-insulationbattsview'),
    path('hti-polycarbonateroofing/', PolycarbonateRoofingView, name='hti-polycarbonateroofing'),
    path('hti-flashing/', FlashingView, name='hti-flashing'),
    path('hti-metalroofinsulationview/', MetalRoofInsulationView, name='hti-metalroofinsulationview'),

]