# forms.py
from django import forms
from .models import FamilyList

class FamilyListForm(forms.ModelForm):
    class Meta:
        model = FamilyList
        fields = ['family_name', 'location', 'contact_address', 'no_of_family_members', 'family_bio']
        widgets = {
            'family_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Family Name'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location'}),
            'contact_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Address'}),
            'no_of_family_members': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Number of Family Members'}),
            'family_bio': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Family Bio'}),
        }
