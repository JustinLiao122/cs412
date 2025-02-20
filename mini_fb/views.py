## mini_fb/views.py
## veiw functions/classes to control data flow between templates and model


from django.shortcuts import render
from django.views.generic import ListView , DetailView
# Create your views here.
from .models import Profile

class ShowAllProfilesView(ListView):

    model = Profile 
    template_name = "mini_fb/show_all_profiles.html"
    context_object_name = "profiles"
    

class ShowProfilePageView(DetailView):

    model = Profile 
    template_name = "mini_fb/show_profile.html"
    context_object_name = "profile"
