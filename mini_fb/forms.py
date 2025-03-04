
# File: mini_fb/forms.py
# Author: Justin Liao (liaoju@bu.edu), 3/4/2025
# Description: defines Django class ModelForms that correspond to models in the models.py, 


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


class UpdateProfileForm(forms.ModelForm):
    '''A form to update a Profile in database.'''

    class Meta:
        '''associate this form with the Profile model; select fields without first and last name as those should not bechangable. '''
        model = Profile
        fields = [ 'city', 'email' ,'image_url' , 'bios']



class UpdateStatusForm(forms.ModelForm):
    
    '''A form to update a Status in database.'''

    class Meta:
        '''associate this form with the StatusMessage model;'''
        model = StatusMessage
        fields = [ 'message' ]




