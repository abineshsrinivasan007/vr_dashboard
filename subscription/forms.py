# subscription/forms.py
from django import forms
from .models import Subscription

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['college_name', 'email', 'password']
        widgets = {'password': forms.PasswordInput()}
