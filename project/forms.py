


from django import forms
from .models import *

class CreateCartForm(forms.ModelForm):
     '''A form to add a Profile to the database.'''

    
     class Meta:
        '''associate this form with the Profile model; select fields.'''
        model = Cart
        fields = ['name']
