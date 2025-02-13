#restaurant/veiw.py
# veiw functions for handling url requests

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
import time
import random 


#list for all the dailies that rotate
dailies = ["Burger: $10" , "Sandwich: $10" , "Wings: $10" ]

def home_page(request):
    '''home_page where it takes in a picture as a context and loads up base html'''
    template_name = 'restaurant/base.html'

    #context variables for html scriplet code
    context= {
        "time": time.ctime(),
         "pictures": "pizza.jpg",
      

    }

    return render(request, template_name , context)




def main(request):
    '''main page takes in a picture as a context and loads up main html'''
    template_name = 'restaurant/main.html'

    context= {
        "time": time.ctime(),
        "pictures": "pizza.jpg",
      

    }

    return render(request, template_name , context)


def order(request):
    '''order form where it displays the order with context variable for the daily special'''
    template_name = 'restaurant/order.html'

    context= {
        "time": time.ctime(),
        "special": random.choice(dailies)

    }

    return render(request, template_name , context)


def confirmation(request):
    '''process the form and generate a result'''
    template_name = 'restaurant/confirmation.html'


    #check if Post data was sent with the HTTP POST message
    if request.POST:

        #counter for total cost
        total = 0

        #extract items feild from form if submitted
        items = []
        if request.POST.get('food1'):
            items.append(request.POST['food1'])
            total += 9
        if request.POST.get('food2'):
            items.append(request.POST['food2'])
            total += 4
        if request.POST.get('food3'):
            items.append(request.POST['food3'])
            total += 12
        if request.POST.get('food4'):
            items.append(request.POST['food4'])
            total += 12


        #extract toppings feild from form if submitted

        toppings = []

        if request.POST.get('topping1'):
            toppings.append(request.POST['topping1'])
            total += 1
        if request.POST.get('topping2'):
            toppings.append(request.POST['topping2'])
            total += 1
        if request.POST.get('topping3'):
            toppings.append(request.POST['topping3'])
            total += 1
        if request.POST.get('topping4'):
            toppings.append(request.POST['topping4'])
            total += 1

        #extract daily special feild from form if submitted
        special = []
        
        if request.POST.get('special1'):
            special.append(request.POST['special1'])
            total += 10
        
        #extract information feild from form not if sumbbmitted because it is required
        name = request.POST.get('Name')
        phone = request.POST.get('Phone')
        email = request.POST.get('Email')


        #extract instructions feild from form if submitted
        Instructions = []
        if request.POST.get('Instructions', ''):
            Instructions.append(request.POST.get('Instructions', ''))


        context= {
            "time": time.ctime( (random.randint(30, 60) * 60)+ time.time())  ,#to add a random amount of time from 30-60 mintues to current time
            "items":items,
            "toppings": toppings,
            "special":special if special != [] else None, #checks if there was a response if not set as None so the scriptlet in html can work with if statment. was having issue with it so this was the alrenative
            "name":name,
            "phone":phone,
             "email":email,
             "instructions":Instructions if Instructions != [] else None,
             "total":total ,
        

        }

    return render(request, template_name , context)