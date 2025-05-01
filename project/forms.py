
# File: project/forms.py
# Author: Justin Liao (liaoju@bu.edu), 4/14/2025
# Description: defines Django class ModelForms that correspond to models in the models.py


from django import forms
from .models import *

class CreateCartForm(forms.ModelForm):
     '''A form to add a Cart to the database.'''

    
     class Meta:
        '''associate this form with the Cart model; select fields.'''
        model = Cart
        fields = ['name']






class CreateCustomerForm(forms.ModelForm):
     '''A form to add a Customer to the database.'''

    
     class Meta:
        '''associate this form with the Customer model; select fields.'''
        model = Customer
        fields = ['firstname', 'lastname', 'address', 'email' ]



class RenameCartForm(forms.ModelForm):
     '''A form to rename a cart in the database.'''

    
     class Meta:
        '''associate this form with the Cart model; select fields.'''
        model = Cart
        fields = ['name']