from django.shortcuts import render

from .models import FooterContent

def DeliveryView(request):
    context = getContext('Delivery')

    return render(request, "footer-content.html", context)

def TOSView(request):
    context = getContext('Terms & Conditions Of Use')

    return render(request, "footer-content.html", context)

def FAQView(request):
    context = getContext('Frequently Asked Questions')

    return render(request, "footer-content.html", context)

def RefundView(request):
    context = getContext('Refund Policy')

    return render(request, "footer-content.html", context)

def WarrantyView(request):
    context = getContext('Warranty')

    return render(request, "footer-content.html", context)

def ColourbondColoursView(request):
    context = getContext('Colourbond Colours')

    return render(request, "footer-content.html", context)

def TechnicalView(request):

    return render(request, "technical-centre.html", {})

# 

def MetalRoofingSheetsView(request):
    context = getContext('How To Install Metal Roofing Sheets')

    return render(request, "footer-content.html", context)

def GutteringView(request):
    context = getContext('How To Install Guttering')

    return render(request, "footer-content.html", context)

def EavesGutteringView(request):
    context = getContext('How To Install Eaves Guttering')

    return render(request, "footer-content.html", context)

def InsulationBattsView(request):
    context = getContext('How To Install Insulation Batts')

    return render(request, "footer-content.html", context)

def PolycarbonateRoofingView(request):
    context = getContext('How To Install Polycarbonate Roofing')

    return render(request, "footer-content.html", context)

def FlashingView(request):
    context = getContext('How To Install Flashing')

    return render(request, "footer-content.html", context)

def MetalRoofInsulationView(request):
    context = getContext('How To Install Metal Roof Insulation')

    return render(request, "footer-content.html", context)

# 

def getContext(page):
    data = FooterContent.objects.get(page=page)

    context = {
        'page': data.page,
        'meta_title': data.meta_title,
        'meta_description': data.meta_description,
        'content': data.content,
    }

    return context
