from django import forms
from django.conf import settings
from .models import Address

from bootstrap_datepicker_plus import DatePickerInput
from datetime import date, datetime, timedelta


class CheckoutForm(forms.Form):

    email = forms.CharField(
                widget=forms.TextInput(
                    attrs={
                        'id': 'email',
                        'class': 'form-control mt-2',
                        'type': 'email',
                        'placeholder': 'Your Email Address',
                        'required': 'true',
                    }
                ),
                label='EMAIL',
                max_length=100,
            )

    first_name = forms.CharField(
                    widget=forms.TextInput(
                        attrs={ 'id': 'first_name',
                                'class': 'form-control mt-2',
                                'type': 'first name', 
                                'placeholder': 'Your Name',
                                'required': 'true'}
                    ),
                    label='FIRST NAME',
                    max_length=50,
                )
    last_name = forms.CharField(
                    widget=forms.TextInput(
                        attrs={ 'id': 'last_name',
                                'class': 'form-control mt-2',
                                'type': 'last name',
                                'placeholder': 'Your Last Name',
                                'required': 'true'}
                    ),
                    label='LAST NAME',
                    max_length=50,
                )
    phone_number = forms.CharField(
                    widget=forms.TextInput(
                        attrs={ "id": "phone_number",
                                "class": "form-control mt-2",
                                "placeholder": "e.g. 0412 345 678",
                                "type": "tel",
                                "minlength": "10",
                                "pattern": "[0-9]+",
                                'required': 'true',}
                    ),
                    label='PHONE NUMBER',
                    max_length=50,
                )
    autocomplete = forms.CharField(
                    required=False, 
                    max_length=120, 
                    label='DELIVERY ADDRESS', 
                    widget=forms.TextInput(
                        attrs={
                            'id': "autocomplete",
                            'class': 'form-control mt-2', 
                            'placeholder': 'e.g. 123 Main Street Melbourne',
                            'autocomplete': 'new-password',}))
    address_line_1 = forms.CharField(
                    max_length=200,
                    label='ADDRESS',
                    widget=forms.TextInput(
                        attrs={
                            'id': "address_line_1", 
                            'class': 'form-control mt-2', 
                            'placeholder': 'e.g. 123 Main Street Melbourne',
                            'required': 'true',
                            'name': 'address_line_1',}))
    city = forms.CharField(
            max_length=100,
            label='SUBURB',
            widget=forms.TextInput(
                attrs={
                    "id": "city",
                    "class": "form-control mt-2",
                    "placeholder": "e.g. Richmond",
                    'required': 'true'
                }
            ),
        )
    state = forms.CharField(
            max_length=15,
            label='STATE',
            widget=forms.TextInput(
                attrs={
                    "id": "state",
                    "class": "form-control mt-2",
                    "readonly": 'readonly',
                    'required': 'true'
                }
            ),
        )
    postal_code = forms.CharField(
            max_length=10,
            label='POST CODE',
            widget=forms.TextInput(
                attrs={
                    "id": "postal_code",
                    "class": "form-control mt-2",
                    "placeholder": "e.g. 1234",
                    'pattern': '[0-9]*',
                    'required title': "Four Digit Post Code",
                    'required': 'true'
                }
            ),
        )
    delivery_instructions = forms.CharField(
            required=False,
            max_length=500,
            label='DELIVERY NOTES',
            widget=forms.Textarea(
                attrs={
                    "id": "delivery_instructions",
                    "class": "form-control mt-2",
                    "placeholder": "Let us know your delivery instructions",
                    "rows": 4,
                }
            ))
    billing_first_name = forms.CharField(
                    required=False,
                    widget=forms.TextInput(
                        attrs={ 'id': 'billing_first_name',
                                'class': 'form-control mt-2',
                                'type': 'first name', 
                                'placeholder': 'Your first name',
                                }
                    ),
                    label='FIRST NAME',
                    max_length=50,
                )
    billing_last_name = forms.CharField(
                    required=False,
                    widget=forms.TextInput(
                        attrs={ 'id': 'billing_last_name',
                                'class': 'form-control mt-2',
                                'type': 'last name',
                                'placeholder': 'Your last name',
                                }
                    ),
                    label='LAST NAME',
                    max_length=50,
                )
    billing_phone_number = forms.CharField(
                    required=False,
                    widget=forms.TextInput(
                        attrs={ "id": "billing_phone_number",
                                "class": "form-control mt-2",
                                "placeholder": "e.g. 0412 345 678",
                                "type": "tel",
                                "minlength": "10",
                                "pattern": "[0-9]+",
                        }
                    ),
                    label='PHONE NUMBER',
                    max_length=50,
                )
    billing_address_line_1 = forms.CharField(
                    required=False,
                    max_length=200,
                    label='ADDRESS',
                    widget=forms.TextInput(
                        attrs={
                            'id': "billing_address_line_1", 
                            'class': 'form-control mt-2', 
                            'placeholder': 'e.g. 123 Main Street Melbourne',
                        }
                    )
    )
    billing_city = forms.CharField(
            max_length=100,
            label='SUBURB',
            required=False,
            widget=forms.TextInput(
                attrs={
                    "id": "billing_city",
                    "class": "form-control mt-2",
                    "placeholder": "e.g. Richmond",
                }
            ),
        )
    billing_state = forms.CharField(
            max_length=15,
            label='STATE',
            required=False,
            widget=forms.TextInput(
                attrs={
                    "id": "billing_state",
                    "class": "form-control mt-2",
                    "placeholder": "e.g. Victoria",
                }
            ),
        )
    billing_postal_code = forms.CharField(
            max_length=10,
            label='POST CODE',
            required=False,
            widget=forms.TextInput(
                attrs={
                    "id": "billing_postal_code",
                    "class": "form-control mt-2",
                    "placeholder": "e.g. 1234",
                    'pattern': '[0-9]*',
                }
            ),
        )
    billing_country = forms.CharField(
        max_length=100,
        label='COUNTRY',
        required=False,
        widget=forms.TextInput(
                attrs={
                    "id": "billing_country",
                    "class": "form-control mt-2",
                    "placeholder": "e.g. Australia",
                }
        )
    )
    postage = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.HiddenInput(
            attrs={
                "id": "postage"
            })
    )
    stripe_token = forms.CharField(
        max_length=250,
        required=False,
        widget=forms.HiddenInput(
            attrs={
                'id': 'stripe_token'
            })
    )
    delivery_date = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.HiddenInput(
            attrs={
                "id": "date_hidden_input",
                "value": "ASAP",
            }),
    )

    order_instructions = forms.CharField(
            required=False,
            max_length=500,
            label='Comments',
            widget=forms.Textarea(
                attrs={
                    "id": "order_instructions",
                    "class": "form-control mt-2",
                    "placeholder": "Is there anything we need to know about your order.",
                    "rows": 4,
                }
            ))