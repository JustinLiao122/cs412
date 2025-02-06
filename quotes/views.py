from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
import time
# Create your views here.
import random 
# Create your views here.


pictures = ["phelps1.jpg","phelps2.jpg","phelps3.jpg","phelps4.jpg","phelps5.jpg","phelps6.jpg"

]


quotes = ["Things won’t go perfect. It’s all about how you adapt from those things and learn from mistakes.", "I like to just think of myself as a normal person who just has a passion, has a goal and a dream and goes out and does it. And that’s really how I’ve always lived my life."
          ,"You can’t put a limit on anything. The more you dream, the farther you get." ,"If you want to be the best, you have to do things that other people aren’t willing to do." , "I want to test my maximum and see how much I can do." ,
          "So many people along the way, whatever it is you aspire to do, will tell you it can’t be done. But all it takes is imagination. You dream. You plan. You reach."]

def home_page(request):
    template_name = 'quotes/base.html'

    context= {
        "time": time.ctime(),
        "letter1": chr(random.randint(65,90)),
        "letter2": chr(random.randint(65,90)),
        "number": random.randint(1,10),
        "pictures":random.choice(pictures),
        "quotes": random.choice(quotes),

    }

    return render(request, template_name , context)


def quote(request):
    template_name = 'quotes/quote.html'

    context= {
        "time": time.ctime(),
        "letter1": chr(random.randint(65,90)),
        "letter2": chr(random.randint(65,90)),
        "number": random.randint(1,10),
        "pictures":random.choice(pictures),
        "quotes": random.choice(quotes),

    }

    return render(request, template_name , context)


def show(request):
    template_name = 'quotes/show_all.html'

    context= {
        "time": time.ctime(),
        "letter1": chr(random.randint(65,90)),
        "letter2": chr(random.randint(65,90)),
        "number": random.randint(1,10),
        "quote1": "Things won’t go perfect. It’s all about how you adapt from those things and learn from mistakes.",
        "quote2": "I like to just think of myself as a normal person who just has a passion, has a goal and a dream and goes out and does it. And that’s really how I’ve always lived my life.",
        "quote3": "You can’t put a limit on anything. The more you dream, the farther you get.",
        "quote4": "If you want to be the best, you have to do things that other people aren’t willing to do.",
        "quote5": "I want to test my maximum and see how much I can do.",
        "quote6":"So many people along the way, whatever it is you aspire to do, will tell you it can’t be done. But all it takes is imagination. You dream. You plan. You reach." ,
        "image1":"phelps1.jpg"  ,     
        "image2":"phelps2.jpg"   , 
        "image3":"phelps3.jpg"    ,
        "image4":"phelps4.jpg"    ,
        "image5":"phelps5.jpg"   ,
        "image6":"phelps6.jpg"    ,                                                                                                                      



    }

    return render(request, template_name , context)

def aboutquotes(request):
    template_name = 'quotes/about.html'

    context= {
        "time": time.ctime(),
        "letter1": chr(random.randint(65,90)),
        "letter2": chr(random.randint(65,90)),
        "number": random.randint(1,10),
        "about": "Micheal Phelps is one of if not the greatest swimmer to exsist. He deciated his whole life to becoming the top swimmer in the world. He has accumulated 23 gold metals throughout his carreer. He made the Olympic team when he was 15 and won his first gold in Athens, 2004" ,
        "author" : "Justin Liao"
    }

    return render(request, template_name , context)