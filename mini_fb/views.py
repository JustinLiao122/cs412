# File: mini_fb/views.py
# Author: Justin Liao (liaoju@bu.edu), 3/4/2025
# Description: veiw functions/classes to control data flow between templates and model


from django.shortcuts import render 
from django.views.generic import ListView , DetailView ,CreateView ,UpdateView,DeleteView
from django.urls import reverse

# Create your views here.
from .models import Profile ,Image , StatusImage,StatusMessage

from .forms import CreateProfileForm ,CreateStatusMessageForm,UpdateProfileForm,UpdateStatusForm




class ShowAllProfilesView(ListView):
    #class that inhierts from the generic ListView and interacts with the model Profile 
    # and gives the data to the template listed wiht the context name profiles

    model = Profile 
    template_name = "mini_fb/show_all_profiles.html"
    context_object_name = "profiles"
    

class ShowProfilePageView(DetailView):

    #class that inhierts from the  DetailView and interacts with the model Profile 
    # and gives the approate data of the spesific profile to the template listed wiht the context name profiles
    model = Profile 
    template_name = "mini_fb/show_profile.html"
    context_object_name = "profile"



class CreateProfileView(CreateView):

    #class that inhierts from the  CreateView and interacts with the form class CreaProfileForm rendering the profile creation form 
    form_class = CreateProfileForm
    template_name = "mini_fb/create_profile_form.html"



class CreateStatusMessageView(CreateView):


        #class that inhierts from the  CreateView and interacts with the form class CreateStatusMessage rendering the status creation form 
    form_class = CreateStatusMessageForm
    template_name = "mini_fb/create_status_form.html"



    def get_context_data(self ,):
        '''Return the dictionary of context variables for use in the template.'''

        # calling the superclass method
        context = super().get_context_data()

        # find/add the profile to the context data
        # retrieve the PK from the URL pattern
        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)

        # add this profile into the context dictionary:
        context['profile'] = profile
        return context

    def form_valid(self, form):
        '''This method handles the form submission and saves the 
        new object to the Django database.
        We need to add the foreign key (of the Article) to the Comment
        object before saving it to the database.
        '''
        
		# instrument our code to display form fields: 
        print(f"CreateCommentView.form_valid: form.cleaned_data={form.cleaned_data}")



        # retrieve the PK from the URL pattern
        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)
        # attach this profile to the comment
        form.instance.profile = profile # set the FK


         # save the status message to database
        sm = form.save()


        # read the file from the form:
        files = self.request.FILES.getlist('files')

        #iterates through all the files if there are any
        for file in files: 

            #creates a Image object with the correct corresponding profile with the file and saves the Image object 
            image = Image(profile = profile , imageField = file)
            image.save()

            #creates a StatusImage object with the correct corresponding statusMessage with the file and saves the StatusImage object 
            statusImage = StatusImage(image = image , statusMessage = sm)
            statusImage.save()
        
        



        # delegate the work to the superclass method form_valid:
        return super().form_valid(form)

    def get_success_url(self):
        '''Provide a URL to redirect to after creating a new StatusMessage.'''

        # create and return a URL:
        # retrieve the PK from the URL pattern
        pk = self.kwargs['pk']
        # call reverse to generate the URL for this Profile with new message
        return reverse('show_profile', kwargs={'pk':pk})





class UpdateProfileView(UpdateView):

    #class that inhierts from the  UpdateView and interacts with the form class UpdateProfileForm rendering the update_profile_form html 
    model = Profile
    form_class = UpdateProfileForm
    template_name = "mini_fb/update_profile_form.html"

    def get_context_data(self ,):
        '''Return the dictionary of context variables for use in the template.'''

        # calling the superclass method
        context = super().get_context_data()

        # find/add the profile to the context data
        # retrieve the PK from the URL pattern
        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)

        # add this profile into the context dictionary:
        context['profile'] = profile
        return context
    
    def get_success_url(self):
        '''Provide a URL to redirect to after updating the profile.'''

        # create and return a URL:
        # retrieve the PK from the URL pattern
        pk = self.kwargs['pk']
        # call reverse to generate the URL for this Profile with new message
        return reverse('show_profile', kwargs={'pk':pk})
    



class DeleteStatusMessageView(DeleteView):

    #class that inhierts from the  Delete rendering the delete_status_form html for the confermation page
    template_name = "mini_fb/delete_status_form.html"
    model = StatusMessage
    context_object_name = 'status'





    def get_success_url(self):
        '''Provide a URL to redirect to after updating the profile.'''

        # create and return a URL:
        # retrieve the PK from the URL pattern
        pk = self.kwargs['pk']

        status = StatusMessage.objects.get(pk=pk)

        profile = status.profile
        # call reverse to generate the URL for this Profile with new message
        return reverse('show_profile', kwargs={'pk':profile.pk})





class UpdateStatusMessageView(UpdateView):


    #class that inhierts from the  UpdateView and interactes with the form class UpdateStatusForm rendering 
    # the update_status_form html for the confermation page
    
    model = StatusMessage
    form_class = UpdateStatusForm
    template_name = "mini_fb/update_status_form.html"
    context_object_name = 'status'


    def get_success_url(self):
        '''Provide a URL to redirect to after updating the profile.'''

        # create and return a URL:
        # retrieve the PK from the URL pattern
        pk = self.kwargs['pk']

        status = StatusMessage.objects.get(pk=pk)

        profile = status.profile
        # call reverse to generate the URL for this Profile with new message
        return reverse('show_profile', kwargs={'pk':profile.pk})