# forms.py
from django import forms
from .models import FamilyList, FamilyImage
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm

class FamilyListForm(forms.ModelForm):
    class Meta:
        model = FamilyList
        fields = ['family_name', 'gender', 'location', 'contact_address', 'bank_account', 'family_bio']
        widgets = {
            'family_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Family Name'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location'}),
            'contact_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Address'}),
            'bank_account': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bank Account'}),
            'family_bio': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Family Bio'}),
        }
        
class UserModelForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", 'email', 'username']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'username'})
        }
        
class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})