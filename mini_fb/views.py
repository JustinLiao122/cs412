## mini_fb/views.py
## veiw functions/classes to control data flow between templates and model


from django.shortcuts import render 
from django.views.generic import ListView , DetailView ,CreateView 
from django.urls import reverse

# Create your views here.
from .models import Profile

from .forms import CreateProfileForm ,CreateStatusMessageForm




class ShowAllProfilesView(ListView):
    #class that inhierts from the generic ListView and interacts with the model Profile and gives the data to the template listed wiht the context name profiles

    model = Profile 
    template_name = "mini_fb/show_all_profiles.html"
    context_object_name = "profiles"
    

class ShowProfilePageView(DetailView):

    #class that inhierts from the  DetailView and interacts with the model Profile and gives the approate data of the spesific profile to the template listed wiht the context name profiles
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

        # delegate the work to the superclass method form_valid:
        return super().form_valid(form)

    def get_success_url(self):
        '''Provide a URL to redirect to after creating a new StatusMessage.'''

        # create and return a URL:
        # retrieve the PK from the URL pattern
        pk = self.kwargs['pk']
        # call reverse to generate the URL for this Profile with new message
        return reverse('show_profile', kwargs={'pk':pk})

