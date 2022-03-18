from django.contrib.auth import authenticate, login, get_user_model
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.core.mail import EmailMessage, BadHeaderError

from products.models import Product
from home_page.models import YouTube, Testimonial
from .forms import ContactForm

def view_404(request):
    # make a redirect to homepage
    # you can use the name of url or just the plain link
    return redirect('/') # or redirect('name-of-index-url')

def error_404(request, exception):
    return render(request, '404.html', {})

def error_500(request):
    return render(request, '500.html', {})

def error_500_test(request):
    # Return an "Internal Server Error" 500 response code.
    data = doesntexist

    return render(request, '404.html', {})

def url_update_page(request):
    products = Product.objects.all()

    context = {
        'products': products,
    }

    return render(request, "url_page.html", context)

def home_page(request):

    featured = Product.objects.all().filter(featured=True, active=True)
    videos = YouTube.objects.all()

    context = {
        'featured': featured,
        'videos': videos,
    }
    # if request.user.is_authenticated:
    #     context["premium_content"] = "Only premium user can see"
    return render(request, "home_page.html", context)


def about_page(request):
    context = {
        "title": "About Page",
        "content": "Welcome to the about page."
    }
    return render(request, "home_page.html", context)


def contact_page(request):
    contact_form = ContactForm(request.POST or None)
    context = {
        "title": "Contact Form",
        "content": "Welcome to the contact page.",
        "form": contact_form,
    }

    if contact_form.is_valid():
        name = contact_form.cleaned_data['fullname']
        from_email = contact_form.cleaned_data['email']
        number = contact_form.cleaned_data['number']
        state = request.session.setdefault('state_selected', 'VIC')
        post_code = contact_form.cleaned_data['post_code']
        order_number = contact_form.cleaned_data['order_number']
        content = contact_form.cleaned_data["content"]

        message = (
                  "New contact from: " + name + "\n" + 
                  "--- Users Details ---\n" + 
                  "Email: " + from_email + "\n" + 
                  "Contact number: 0" + str(number) + "\n" +
                  "State: " + state + "\n" + 
                  "Post code: " + str(post_code) + "\n" +
                  "Order number: "  + str(order_number) + "\n" +
                  "Message: " + content
        )
        subject = "Enquiry from " + from_email

        try:
            email = EmailMessage(subject, message, from_email, ['enquiries@metalroofingonline.com.au'], reply_to=[from_email])
            email.send(fail_silently=False)
        except BadHeaderError:
            return HttpResponse("Invalid header found.")

        if request.is_ajax():
            return JsonResponse({"message": "Thank you for your submission"})

    if contact_form.errors:
        errors = contact_form.errors.as_json()
        if request.is_ajax():
            return HttpResponse(errors, status=400, content_type='application/json')

    return render(request, "contact/view.html", context)
