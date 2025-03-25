# File: mini_fb/views.py
# Author: Justin Liao (liaoju@bu.edu), 3/4/2025
# Description: veiw functions/classes to control data flow between templates and model


from django.shortcuts import render ,redirect
from django.views.generic import ListView , DetailView ,CreateView ,UpdateView,DeleteView , View
from django.urls import reverse

# Create your views here.
from .models import Profile ,Image , StatusImage,StatusMessage

from .forms import CreateProfileForm ,CreateStatusMessageForm,UpdateProfileForm,UpdateStatusForm
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login




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


    def get_context_data(self, **kwargs):
        #gives the html a context varaible for the UserCreationForm
        context = super().get_context_data(**kwargs)
        context['user_form'] = UserCreationForm()  
        return context
    

    def form_valid(self, form):
        #Reconstruct the UserCreationForm from POST data
        user_form = UserCreationForm(self.request.POST)
        
        # Check if it's valid
        if user_form.is_valid():
            #Save the user
            user = user_form.save()
            
            # Attach user to profile before saving
            form.instance.user = user
            
            # log the user in 
            login(self.request, user)
            
            #Save profile and redirect
            return super().form_valid(form)
        else:
            # If user form not valid, re-render the form with errors
            return self.form_invalid(form)

   

class CreateStatusMessageView(LoginRequiredMixin,CreateView):


     #class that inhierts from the  CreateView and interacts with the form class CreateStatusMessage rendering the status creation form 
    form_class = CreateStatusMessageForm
    template_name = "mini_fb/create_status_form.html"


    def get_login_url(self) -> str:
        #redircets the use to the login page if they are not logged in already this is from LoginRequiredMixin
        '''return the URL required for login'''
        return reverse('login') 
    

    def get_object(self):
        #this is a method that finds the profile that is asscoicated with the logged in user
        return Profile.objects.get(user=self.request.user)


    def get_context_data(self ,):
        '''Return the dictionary of context variables for use in the template.'''

        # calling the superclass method
        context = super().get_context_data()

        #retrive the profile from get_object
        profile = self.get_object()


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



        #retrive the profile from get_object
        profile = self.get_object()
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

        #retrive the profile from get_object
        profile = self.get_object()
        pk = profile.pk
        # call reverse to generate the URL for this Profile with new message
        return reverse('show_profile', kwargs={'pk':pk})





class UpdateProfileView(LoginRequiredMixin, UpdateView):

    #class that inhierts from the  UpdateView and interacts with the form class UpdateProfileForm rendering the update_profile_form html 
    model = Profile
    form_class = UpdateProfileForm
    template_name = "mini_fb/update_profile_form.html"
    
    def get_login_url(self) -> str:
        #redircets the use to the login page if they are not logged in already this is from LoginRequiredMixin
        '''return the URL required for login'''
        return reverse('login') 
    
    def get_object(self):
        #this is a method that finds the profile that is asscoicated with the logged in user
        return Profile.objects.get(user=self.request.user)


    def get_context_data(self ,):
        '''Return the dictionary of context variables for use in the template.'''

        # calling the superclass method
        context = super().get_context_data()

        #retrive the profile from get_object
        profile = self.get_object()


        # add this profile into the context dictionary:
        context['profile'] = profile
        return context
    
    def get_success_url(self):
        '''Provide a URL to redirect to after updating the profile.'''
        #retrive the profile from get_object
        profile = self.get_object()
        pk = profile.pk
        # call reverse to generate the URL for this Profile with new message
        return reverse('show_profile', kwargs={'pk':pk})
    



class DeleteStatusMessageView(LoginRequiredMixin,DeleteView):

    #class that inhierts from the  Delete rendering the delete_status_form html for the confermation page
    template_name = "mini_fb/delete_status_form.html"
    model = StatusMessage
    context_object_name = 'status'


    def get_login_url(self) -> str:
            #redircets the use to the login page if they are not logged in already this is from LoginRequiredMixin
        '''return the URL required for login'''
        return reverse('login') 



    def get_success_url(self):
        '''Provide a URL to redirect to after updating the profile.'''

        # create and return a URL:
        # retrieve the PK from the URL pattern
        pk = self.kwargs['pk']

        status = StatusMessage.objects.get(pk=pk)

        profile = status.profile
        # call reverse to generate the URL for this Profile with new message
        return reverse('show_profile', kwargs={'pk':profile.pk})





class UpdateStatusMessageView(LoginRequiredMixin, UpdateView):


    #class that inhierts from the  UpdateView and interactes with the form class UpdateStatusForm rendering 
    # the update_status_form html for the confermation page
    
    model = StatusMessage
    form_class = UpdateStatusForm
    template_name = "mini_fb/update_status_form.html"
    context_object_name = 'status'


    def get_login_url(self) -> str:
        #redircets the use to the login page if they are not logged in already this is from LoginRequiredMixin
        '''return the URL required for login'''
        return reverse('login') 
    
    def get_success_url(self):
        '''Provide a URL to redirect to after updating the profile.'''

        # create and return a URL:
        # retrieve the PK from the URL pattern
        pk = self.kwargs['pk']

        status = StatusMessage.objects.get(pk=pk)

        profile = status.profile
        # call reverse to generate the URL for this Profile with new message
        return reverse('show_profile', kwargs={'pk':profile.pk})
    






class AddFriendView(LoginRequiredMixin,View):
    # a class that inherits from the generic superclass django.views.generic.View 



    def get_login_url(self) -> str:
        #redircets the use to the login page if they are not logged in already this is from LoginRequiredMixin
        '''return the URL required for login'''
        return reverse('login') 

    def dispatch(self, request, *args, **kwargs):
        # overriding the dispatch method by reading the URL parameters from kwargs we can take the two profiles 
        # iven from the url and add them as frineds and return the user back to the profile it was on

        #takes the profile pk from the url and stores them
        
        profile2_pk = self.kwargs.get('other_pk')

        #retrive the profile from get_object
        profile1 = self.get_object()

        profile2 = Profile.objects.get(pk = profile2_pk)

        #adding the two profiles as friends
        profile1.add_friend(profile2)

        # returning user to orginal profile
        return redirect(reverse('show_profile', kwargs={'pk': profile1.pk}))
    
    def get_object(self):
        #this is a method that finds the profile that is asscoicated with the logged in user

        return Profile.objects.get(user=self.request.user)



class ShowFriendSuggestionsView(LoginRequiredMixin,DetailView):
    # class that inhierts from the  DetailView and interactes with the model Profile rendering 
    # the friend_suggestions.html and passes a context called profile
    
    template_name = "mini_fb/friend_suggestions.html"
    model = Profile
    context_object_name = 'profile'

    def get_login_url(self) -> str:
        #redircets the use to the login page if they are not logged in already this is from LoginRequiredMixin

        '''return the URL required for login'''
        return reverse('login') 
    
    def get_object(self):
        #this is a method that finds the profile that is asscoicated with the logged in user

        return Profile.objects.get(user=self.request.user)

class ShowNewsFeedView(DeleteView):

    # class that inhierts from the  DetailView and interactes with the model Profile rendering 
    # the news_feed.html and passes a context called profile

    template_name = "mini_fb/news_feed.html"
    model = Profile
    context_object_name = 'profile'

    def get_object(self):
        #this is a method that finds the profile that is asscoicated with the logged in user

        return Profile.objects.get(user=self.request.user)