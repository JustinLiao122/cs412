#mini_fb/forms.py

from django import forms
from .models import Profile, StatusMessage



class CreateProfileForm(forms.ModelForm):
     '''A form to add a Profile to the database.'''

    
     class Meta:
        '''associate this form with the Profile model; select fields.'''
        model = Profile
        fields = ['firstname', 'lastname', 'city', 'email' ,'image_url' , 'bios']



class CreateStatusMessageForm(forms.ModelForm):

     '''A form to add a StatusMessage to the database.'''

     class Meta:
        '''associate this form with the StatusMessage model; select fields.'''
        model = StatusMessage
        fields = ['message']




