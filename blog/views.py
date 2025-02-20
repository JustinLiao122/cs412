from django.shortcuts import render
from django.views.generic import ListView
# Create your views here.
from .models import Article

class ShowAllView(ListView):

    model = Article 
    template_name = "blog/show_all.html"
    context_object_name = "articles"
    
