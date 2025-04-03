# File: voter_analytics/views.py
# Author: Justin Liao (liaoju@bu.edu), 4/3/2025
# Description: veiw functions/classes to control data flow between templates and model


from django.shortcuts import render ,redirect
from django.views.generic import ListView , DetailView ,CreateView ,UpdateView,DeleteView , View
from django.urls import reverse
from django.db.models.query import QuerySet

# Create your views here.
from .models import*
import plotly
import plotly.graph_objs as go
from django.db.models import Count


#from .forms import CreateProfileForm ,CreateStatusMessageForm,UpdateProfileForm,UpdateStatusForm
#from django.contrib.auth.mixins import LoginRequiredMixin 
#from django.contrib.auth.forms import UserCreationForm
#from django.contrib.auth import login


class ShowAllVotersView(ListView):
    #class that inhierts from the generic ListView and interacts with the model Voter 
    # and gives the data to the template listed wiht the context name voters

    model = Voter 
    template_name = "voter_analytics/voter_list.html"
    context_object_name = "voters"
    paginate_by = 50


    def get_queryset(self):
        # THis method is used to query the database and filter the voters based on the submisson of the form in the url
            
        results = super().get_queryset()

        # filter results by these field(s):
        if 'party_affiliation' in self.request.GET:
            party= self.request.GET['party_affiliation']
            if party:
                results = results.filter(party=party)
        if 'Voter_Score' in self.request.GET:
            score= self.request.GET['Voter_Score']
            if score:
                results = results.filter(score=int(score))
        if 'min_year' in self.request.GET:
            min_year= self.request.GET['min_year']
            if min_year:
                results = results.filter(dob__year__gte=min_year)
        if 'max_year' in self.request.GET:
            max_year= self.request.GET['max_year']
            if max_year:
                results = results.filter(dob__year__lte=max_year)

        if 'v20state' in self.request.GET:
            v20state= self.request.GET['v20state']
            if v20state:
                results = results.filter(v20state=True)

        if 'v21town' in self.request.GET:
            v21town= self.request.GET['v21town']
            if v21town:
                results = results.filter(v21town=True)
        
        if 'v21primary' in self.request.GET:
            v21primary= self.request.GET['v21primary']
            if v21primary:
                results = results.filter(v21primary=True)
        if 'v22general' in self.request.GET:
            v22general= self.request.GET['v22general']
            if v22general:
                results = results.filter(v22general=True)

        if 'v2v23town0state' in self.request.GET:
            v23town= self.request.GET['v23town']
            if v23town:
                results = results.filter(v23town=True)

        return results


    def get_context_data(self, **kwargs):
            #THis method passes context varables to the template so that they can be used in the html
            # calling the superclass method
            context = super().get_context_data(**kwargs)

            #filters all the Voters by party and get all distinct values so that the form can have a dropdown menu of all parties
            context['partys'] = Voter.objects.values_list('party', flat=True).distinct()
            # for the years 
            context['years'] = range(1920, 2005)
            #print(context)
            #print("HEhfwiehfwehfowehfoiwefoiwehfoiwehfoiwehf")
            return context
    



class VoterDetailView(DetailView):
     #class that inhierts from the generic DetailView and interacts with the model Voter 
    # and gives the data to the template listed wiht the context name voter

    model = Voter 
    template_name = "voter_analytics/show_voter.html"
    context_object_name = "voter"




class GraphBetailView(ListView):
   #class that inhierts from the generic ListView and interacts with the model Voter 
    # and gives the data to the template listed wiht the context name voters

    model = Voter 
    template_name = "voter_analytics/graphs.html"
    context_object_name = "voters"

    def get_queryset(self):
        # THis method is used to query the database and filter the voters based on the submisson of the form in the url
        results = super().get_queryset()

        # filter results by these fields
        if 'party_affiliation' in self.request.GET:
            party= self.request.GET['party_affiliation']
            if party:
                results = results.filter(party=party)
        if 'Voter_Score' in self.request.GET:
            score= self.request.GET['Voter_Score']
            if score:
                results = results.filter(score=int(score))
        if 'min_year' in self.request.GET:
            min_year= self.request.GET['min_year']
            if min_year:
                results = results.filter(dob__year__gte=min_year)
        if 'max_year' in self.request.GET:
            max_year= self.request.GET['max_year']
            if max_year:
                results = results.filter(dob__year__lte=max_year)

        if 'v20state' in self.request.GET:
            v20state= self.request.GET['v20state']
            if v20state:
                results = results.filter(v20state=True)

        if 'v21town' in self.request.GET:
            v21town= self.request.GET['v21town']
            if v21town:
                results = results.filter(v21town=True)
        
        if 'v21primary' in self.request.GET:
            v21primary= self.request.GET['v21primary']
            if v21primary:
                results = results.filter(v21primary=True)
        if 'v22general' in self.request.GET:
            v22general= self.request.GET['v22general']
            if v22general:
                results = results.filter(v22general=True)

        if 'v2v23town0state' in self.request.GET:
            v23town= self.request.GET['v23town']
            if v23town:
                results = results.filter(v23town=True)

        return results



    def get_context_data(self, **kwargs):
            #This method passes context varables that are graphs for the template to display
            # calling the superclass method
            context = super().get_context_data(**kwargs)
            #getting the queryset of all the voters that are filtered by the form 
            qs = self.get_queryset()

            #getting the distinct values of the party field and then counting the number of voters in each party
            partys = qs.values_list('party', flat=True).distinct()

            x = list(partys)
            y = [qs.filter(party=party).count() for party in x]



            fig = go.Pie(
                labels=x,
                values=y,
                domain=dict(x=[0, 1], y=[0, 1])
            )
            title_text = "Voter distribution by party affiliation"

            graph_div_splits = plotly.offline.plot({
                "data": [fig],
                "layout": {
                    "title": title_text,
                    "width": 800,   
                    "height": 800    
                }
            }, auto_open=False, output_type="div")


            #getting the distinct values of the election field and then counting the number of voters in each election
            x2 = ["v20state", "v21town", "v21primary","v22general", "v23town"]
            y2 = [qs.filter(v20state=True).count(),qs.filter(v21town=True).count(), qs.filter(v21primary=True).count(), qs.filter(v22general=True).count(), qs.filter(v23town=True).count()]

            fig = go.Bar(x=x2, y=y2)
            title_text = "Vote Count by Election"
            graph_vote_count = plotly.offline.plot({
                "data": [fig],
                "layout": {
                    "title": title_text,
                    "width": 800,   
                    "height": 800   
                }
            }, auto_open=False, output_type="div")
            



            #getting the distinct values of the year field and then counting the number of voters in each year
            years = (qs.filter(dob__year__gte=1920, dob__year__lte=2004).values('dob__year').annotate(count=Count('id')).order_by('dob__year'))
            year_count = {year['dob__year']: year['count'] for year in years}
            x3 = list(range(1920, 2005))
            y3 = [year_count.get(year, 0) for year in x3]

            fig = go.Bar(x=x3, y=y3)

            title_text = f"Vote distribution by year of birth"
            graph_year = plotly.offline.plot({
                "data": [fig],
                "layout": {
                    "title": title_text,
                    "width": 800,   
                    "height": 800   
                }
            }, auto_open=False, output_type="div")


            context['ByYear'] = graph_year
            context['ByParty'] = graph_div_splits
            context['ByElections'] = graph_vote_count
            context['partys'] = Voter.objects.values_list('party', flat=True).distinct()
            context['years'] = range(1920, 2005)
            #print(context)
            #print("HEhfwiehfwehfowehfoiwefoiwehfoiwehfoiwehf")
            return context
    

