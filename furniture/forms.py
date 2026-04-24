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
        required=True,
        initial=False,
        label='Use same address for delivery as billing',
        error_messages={'required': 'Please select a delivery address option.'}
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
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Name on payment', 'class': 'detail-input'}),
    )
    upi_id = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'yourname@bank', 'class': 'detail-input'}),
    )
    card_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'XXXX XXXX XXXX XXXX', 'class': 'detail-input'}),
    )
    expiry_date = forms.CharField(
        max_length=5,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'MM/YY', 'class': 'detail-input'}),
    )
    cvv = forms.CharField(
        max_length=4,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'CVV', 'class': 'detail-input'}),
    )

    def __init__(self, *args, payment_method='Google Pay', **kwargs):
        self.payment_method = (payment_method or 'Google Pay').strip()
        super().__init__(*args, **kwargs)

    def clean(self):
        data = super().clean()
        upi = (data.get('upi_id') or '').strip()
        
        # We need validation depending on payment method
        if self.payment_method == 'UPI' or self.payment_method == 'Pay via UPI App':
            if not upi:
                self.add_error('upi_id', 'UPI ID is required for UPI payments.')
            elif not re.match(r'^[\w.\-]{2,64}@[\w.\-]{2,64}$', upi):
                self.add_error('upi_id', 'Enter a valid UPI ID (example: yourname@okbank).')
                
        elif self.payment_method == 'Credit / Debit Card':
            card_number = (data.get('card_number') or '').strip()
            if not card_number or len(card_number) < 13:
                self.add_error('card_number', 'Please enter a valid card number.')
            
            expiry_date = (data.get('expiry_date') or '').strip()
            if not re.match(r'^(0[1-9]|1[0-2])\/?([0-9]{4}|[0-9]{2})$', expiry_date):
                self.add_error('expiry_date', 'Please enter a valid expiry date (MM/YY).')
                
            cvv = (data.get('cvv') or '').strip()
            if not cvv or len(cvv) < 3:
                self.add_error('cvv', 'Please enter a valid CVV.')
        return data
