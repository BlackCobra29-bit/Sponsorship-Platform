# forms.py
from django import forms
from .models import FamilyList
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm

class FamilyListForm(forms.ModelForm):
    class Meta:
        model = FamilyList
        fields = ['family_name', 'location', 'contact_address', 'family_bio']
        widgets = {
            'family_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Family Name'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location'}),
            'contact_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Address'}),
            'family_bio': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Family Bio'}),
        }

class UserModelForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
        }
        
class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})