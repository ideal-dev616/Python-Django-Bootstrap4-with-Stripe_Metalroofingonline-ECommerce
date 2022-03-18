from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class ContactForm(forms.Form):
    fullname = forms.CharField(
        label="Name *",
        widget=forms.TextInput(
            attrs={
                    "id": "fullname",
                    "class": "form-control border-LightSteelBlue",
                    "placeholder": "Name"
            }
        )
    )
    email = forms.EmailField(
        label="Email Address *",
        widget=forms.EmailInput(
            attrs={
                "id": "email",
                "class": "form-control border-LightSteelBlue",
                "placeholder": "Email Address"
            }
        )
    )

    post_code = forms.IntegerField(
        label="Postal Code *",
        widget=forms.TextInput(
            attrs={
                "type": "number",
                "id": "post_code",
                "class": "form-control border-LightSteelBlue",
                "placeholder": "Postal Code"
            })
        )

    number = forms.IntegerField(
        label="Contact Number *",
        widget=forms.TextInput(
            attrs={
                "type": "number",
                "id": "number",
                "class": "form-control border-LightSteelBlue",
                "placeholder": "Contact Number*"
            }
        )
    )

    order_number = forms.IntegerField(
        label="Order Number",
        required=False,
        widget=forms.TextInput(
            attrs={
                "type": "number",
                "id": "order_number",
                "class": "form-control border-LightSteelBlue",
                "placeholder": "Order Number*"
            }
        )
    )    

    content = forms.CharField(
        label=" ",
        widget=forms.Textarea(
            attrs={

                "id": 'content',
                'class': 'form-control border-LightSteelBlue',
                "placeholder": "Message"
            }
        )
    )


    # def clean_email(self):
    #     email = self.cleaned_data.get("email")
    #     if not "gmail.com" in email:
    #         raise forms.ValidationError("Email has to be gmail.com")
    #     return email
