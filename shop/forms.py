from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'address_line_1', 'address_line_2', 'city', 'state',
            'postal_code', 'country', 'special_instructions'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control border-0 bg-light',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control border-0 bg-light',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control border-0 bg-light',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control border-0 bg-light',
                'required': True
            }),
            'address_line_1': forms.TextInput(attrs={
                'class': 'form-control border-0 bg-light',
                'required': True,
                'placeholder': 'Street address, P.O. Box, company name, c/o'
            }),
            'address_line_2': forms.TextInput(attrs={
                'class': 'form-control border-0 bg-light',
                'placeholder': 'Apartment, suite, unit, building, floor, etc.'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control border-0 bg-light',
                'required': True
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control border-0 bg-light',
                'required': True
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control border-0 bg-light',
                'required': True
            }),
            'country': forms.Select(attrs={
                'class': 'form-select border-0 bg-light',
                'required': True
            }),
            'special_instructions': forms.Textarea(attrs={
                'class': 'form-control bg-light border-0',
                'style': 'height: 100px',
                'placeholder': 'Any special delivery instructions...'
            }),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove all non-digit characters
            phone = ''.join(filter(str.isdigit, phone))
            if len(phone) < 10:
                raise forms.ValidationError("Phone number must be at least 10 digits.")
        return phone

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code')
        if postal_code:
            postal_code = postal_code.strip()
            if len(postal_code) < 3:
                raise forms.ValidationError("Please enter a valid postal code.")
        return postal_code