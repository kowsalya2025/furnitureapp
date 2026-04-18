import re

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


zip_validator = RegexValidator(
    r'^[A-Za-z0-9\-\s]{3,12}$',
    'Enter a valid postal / ZIP code.',
)


class CheckoutForm(forms.Form):
    first_name = forms.CharField(
        max_length=150,
        min_length=2,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. John', 'class': 'checkout-field'}),
    )
    last_name = forms.CharField(
        max_length=150,
        min_length=1,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Doe', 'class': 'checkout-field'}),
    )
    country = forms.CharField(
        max_length=100,
        min_length=2,
        widget=forms.TextInput(attrs={'placeholder': 'Country', 'class': 'checkout-field'}),
    )
    street_address = forms.CharField(
        max_length=255,
        min_length=5,
        widget=forms.TextInput(attrs={'placeholder': 'Street address', 'class': 'checkout-field'}),
    )
    city = forms.CharField(
        max_length=100,
        min_length=2,
        widget=forms.TextInput(attrs={'placeholder': 'City', 'class': 'checkout-field'}),
    )
    state = forms.CharField(
        max_length=100,
        min_length=2,
        widget=forms.TextInput(attrs={'placeholder': 'State', 'class': 'checkout-field'}),
    )
    zip_code = forms.CharField(
        max_length=12,
        validators=[zip_validator],
        widget=forms.TextInput(attrs={'placeholder': 'Postal / ZIP code', 'class': 'checkout-field'}),
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': 'Phone number', 'class': 'checkout-field', 'type': 'tel'}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email address', 'class': 'checkout-field'}),
    )
    delivery_same_as_billing = forms.BooleanField(
        required=False,
        initial=False,
        label='Use same address for delivery as billing',
    )

    def clean_phone(self):
        raw = self.cleaned_data.get('phone', '')
        digits = ''.join(c for c in raw if c.isdigit())
        if len(digits) < 10:
            raise ValidationError('Enter a phone number with at least 10 digits.')
        return raw.strip()


class PaymentDetailsForm(forms.Form):
    payer_name = forms.CharField(
        max_length=100,
        min_length=2,
        widget=forms.TextInput(attrs={'placeholder': 'Name on payment', 'class': 'detail-input'}),
    )
    upi_id = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'yourname@bank', 'class': 'detail-input'}),
    )

    def __init__(self, *args, payment_method='Google Pay', **kwargs):
        self.payment_method = (payment_method or 'Google Pay').strip()
        super().__init__(*args, **kwargs)

    def clean(self):
        data = super().clean()
        upi = (data.get('upi_id') or '').strip()
        if self.payment_method == 'UPI':
            if not upi:
                self.add_error('upi_id', 'UPI ID is required for UPI payments.')
            elif not re.match(r'^[\w.\-]{2,64}@[\w.\-]{2,64}$', upi):
                self.add_error('upi_id', 'Enter a valid UPI ID (example: yourname@okbank).')
        return data
