# File: project/views.py
# Author: Justin Liao (liaoju@bu.edu), 4/26/2025
# Description: url patterns for the project app



from django.shortcuts import render

# Create your views here.
from django.shortcuts import redirect
from django.urls import reverse

from .models import*
from django.views.generic import ListView , DetailView ,CreateView ,UpdateView,DeleteView , View, TemplateView 
from .forms import* 
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from project.search_client import es
from django.http import HttpResponse
from rapidfuzz import fuzz
from django.db.models import Case, When, IntegerField

import math






class Welcome(TemplateView):
    #class that just shows a templete for the welcome page
    template_name = "project/welcome.html"






class CreateCustomerView(CreateView):
    #Class to create a new customer that inherits from the CreateView and interacts with the CreatCustomerForm class to render in the form to create a new customer

    form_class = CreateCustomerForm
    template_name = "project/create_customer_form.html"


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
            
            # Attach user to customer before saving
            form.instance.user = user
            
            # log the user in 
            login(self.request, user)
            
            #Save profile and redirect
            return super().form_valid(form)
        else:
            # If user form not valid, re-render the form with errors
            return self.form_invalid(form)
        

    def get_success_url(self):
        '''Provide a URL to redirect to after creating a new Customer.'''

     
        # call reverse to redirect to the shop page
        return reverse('shop')
        


class SingleItem(DetailView):
    #class that inherits from DetailView that displays a single instanse of the model item passing context varable item to access the object
    model = Item
    template_name = "project/item.html"
    content_object_name = "item"
    

class Shop(ListView):
    #cladd that inherits from ListView that displays a list of objects from the mdoel Item
    model = Item
    template_name = "project/shop.html"
    context_object_name = "items"
    paginate_by = 50


    def get_queryset(self):
        # THis method is used to query the database and filter the items based on the submisson of the form in the url
            
        results = super().get_queryset()

        #gets the value the user put to search for
        name = self.request.GET.get('q')

        #checks if there is a name 
        if name:
            #tryies to do this search if fails go to default search
            try:

                #I tired to do good search practice with the orm and rapidfussy fucntion but nothign beats the elastic search 
                #here I use a offsite application called bonsi which does elsitc search for you
                #downside is that I need to pass my item models to the application whihc duplicates the data
                #I understand that it may see not optimal but it is standard pratices used by many big companys as it is very fast and efficeny 
                # If I tried to use the django default orm with sqlite3 or even fussy search it is ethier the search is too restricted or it is very very slow 
                # So I decided to keep this in as a faster way ofc another options was to conver my sqlite3 database to a postreSql database but I already defined and created all my view classes based on sqlite

                # Send a search request to the Elasticsearch 'items' index
                # We use multi_match to search across 'name', 'aisle', and 'store' fields
                #Fuzziness 'AUTO' allows for misspellings, and prefix_length=1 ensures at least one character must match exactly
                response = es.search(
                    index="items",
                    body={   
                        "query": {
                            "multi_match": {
                                "query": name,
                                "fields": ["name", "aisle", "store"],
                                "fuzziness": "AUTO",     
                                "prefix_length": 1       
                            }
                        }
                    }
                )
                # Extract matched document IDs from the search results
                hits = response["hits"]["hits"]

                if hits:
                    #if matches are found return the items with there corresponding ids
                    ids = [hit["_id"] for hit in hits]
                    return Item.objects.filter(id__in=ids)
                else:
                    #if maches are not found try default ORM seaching seeing if any items contain this name
                    print("Using default Search")
                    return results.filter(name__icontains=name)

            except Exception as e:
                #if fails or the servers are down try the default ORM contains name 
                print(f"Error connecting to Elasticsearch: {e}")
                print("Using default Search")
                return results.filter(name__icontains=name)
        
        return results



class ActiveCartDetailView(TemplateView):

    #class that inherts form TemplateView and displays the cart.html 
    template_name = "project/cart.html"


    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        #gets the current logged in user
        user = self.request.user
        # match cusmoter with the current logged in user
        customer = Customer.objects.get(user = user)

        try:
            #Try to get the cart that is currently active 
            cart = Cart.objects.get(customer=customer, is_active=True)
        except Cart.DoesNotExist:
            #if there is no cart avitce just set as none to signal the html that there is No carts active
            cart = None

       
        #active cart to display 
        context['cart'] = cart
        #all items in the cart to pass to the html 
        context['cart_items'] = CartItem.objects.filter(cart=cart)
        #all the carts the user has but are not the currently active one that is on display and havent been removed where it is a pastorder 
        context['inactive_carts'] = Cart.objects.filter(customer=customer, is_active=False, removed = False)

        return context

def switch_to_cart(request, cart_id):
    #method to switch which cart is the active displayed cart to the user 


    #gets the cart that the user wants to switch to 
    cart = Cart.objects.get(pk = cart_id)
    #finds the customer 
    customer = cart.customer

    #update all carts to not active so we garentee that only one cart is active at a time
    Cart.objects.filter(customer=customer).update(is_active=False)


    #switch the cart the user selected to active so it displays on the html
    cart.is_active = True
    # save the change
    cart.save()

    #redirct once done to Cart
    return redirect('Cart')  


def remove_from_cart(request, item_id, cart_id):
    #method that removes the item in the cart form the cart 

    #finds the cart the user is on 
    cart = Cart.objects.get(pk = cart_id)
    #finds the item the user wants to delete from the cart
    item = Item.objects.get(pk = item_id)

    print("Cart ID:", cart.id)
    print("Item ID:", item.id)

    #finds the CartItem that relates to the cart and item and deletes the relationship
    cartitem = CartItem.objects.get(cart = cart , item = item )
    if cartitem:
        cartitem.delete()

    #redirect to Cart to display the updated info 
    return redirect('Cart')







def AddToCartView(request, item_id):
    #method to added a certian item to a cart

    #finds the item the user selected that is passed 
    item = Item.objects.get(pk = item_id)
    #finds the current user and finds the coressponding customer
    user = request.user
    customer = Customer.objects.get(user = user)
    #finds the active cart that the user is on right now
    cart = Cart.objects.get(customer = customer, is_active=True)

    #create a CartItem object to define the relationship from cart to item or get it if it already esists
    cartitem, created = CartItem.objects.get_or_create(cart=cart, item=item)
    #check if it was created or if it was grabbed if it was grabbed that means the item was already in the cart so the user wants to add another one so we change the quantity of that item in the cart
    if not created:
        cartitem.quantity += 1
        cartitem.save()

    #return sucess dont need to redirect to anything so the user stays on the same page and what ever section they were scrolled to 
    return HttpResponse(status=204)


class PastOrders(ListView):
    #class that inherits from ListView that displays a list off PastOrder Objects in past_order.html 
    model = PastOrder
    template_name = "project/past_order.html"
    context_object_name = "past_order"
    paginate_by = 50


    def get_queryset(self):
        # THis method is used to query the database and filter the PastOrders based on the lastest to past 

        results = super().get_queryset()
        results = results.order_by("-timestamp")
       
        
        return results



class RenameCartView(LoginRequiredMixin, UpdateView):
    #class that inherits from UpdateView that uses the RenameCartForm to rename the name of the cart
    model = Cart
    form_class = RenameCartForm
    template_name = "project/rename_cart_form.html"
    context_object_name = "cart"


    def get_success_url(self):
        #redirects to cart with the updated name in the database for th cart
        return reverse('Cart') 



# def euclidean(coord1, coord2):
#     return math.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)

# def optimize_path(layout, aisle_list):
#     current = layout["Main"]
#     print("layout: " , layout)
#     aisles_to_visit = aisle_list.copy()
#     ordered_aisles = []

#     while aisles_to_visit:
#         # Find closest aisle
#         next_aisle = min(aisles_to_visit, key=lambda aisle: euclidean(current, layout[aisle]))
#         ordered_aisles.append(next_aisle)
#         current = layout[next_aisle]
#         aisles_to_visit.remove(next_aisle)

#     return ordered_aisles



def best_route( items, start, end ):
        #method to fidn the best route for a certain amount of items with a start and end

        #an empty dictonary to store all the stores and there aisles
        store_aisles = {}
        #empty dictonary to store all the 
        store_items = {}

        #iterate through all the items 
        for item in items:
            #get the store and aisle of this item 
            store = item.store
            aisle = item.aisle

            #check if the store is not in the dict if not add the store and inlize it
            if store not in store_aisles:
                store_aisles[store] = []
            #check if the aisle is not in the store in the dictonary if not add it
            if aisle not in store_aisles[store]:
                store_aisles[store].append(aisle)

            #check if store is not in the dict if not add the store and inlize it
            if store not in store_items:
                store_items[store] = {}
            #chekc if aisle not in the store in the dictonary if not add it
            if aisle not in store_items[store]:
                store_items[store][aisle] = []
            # at the end the store and the aisle should all be added in find the store and aisle and add the item name in the dictonary
            store_items[store][aisle].append(item.name)


        #inlize a empty dict to store all the stores and the optimize aisle path and the full path coords so I can pass them on to display the route on a grid map
        routes_by_store = {}
        for store, aisle_to_visit in store_aisles.items():
            #an empty dictonary to store all the aisles as keys and the items in each aisle as values
            store_aisle_items = {}

            if len(aisle_to_visit) <= 15: 
                route = store.A_star_method( aisle_to_visit, start, end )
            else:
                #going to use cluster routeing less optimal but way faster for greater number of aisle
                #will implment later down the line if I include other stores besides star market as star only has 20 total aisle and dont think users will be needing to vissit all 20 for now
                route = store.A_star_method( aisle_to_visit, start, end )
            #inlize a empty list so I can store the full path of coords 
            full_path = []

            for i in range(len(route) - 1):
                # go through each aisle and find the distance from the current aisle to the next
                start_aisle = route[i]
                end_aisle = route[i + 1]
                #grab all the precomputed aisle distances and path
                aisle_distances = store.aisle_distances
                path_info = aisle_distances[start_aisle][end_aisle]

                #if i is 0 that means to include the start coord 
                if i == 0:
                    full_path.extend(path_info["path"])  
                else:
                    # if i is not 0 that means to not include the start coord as it is already accouted for from the previous calculation
                    full_path.extend(path_info["path"][1:]) 

            
            for aisle in route: 
                #goes through each aisle in route and add the aisle as keys and its items as values if the aisle is the start or end have an empty list as you dont need any items 
                if aisle == start or aisle == end: 
                    store_aisle_items[aisle] = []
                else:
                    store_aisle_items[aisle] = store_items[store][aisle]

            #then add the storename as a string as a key to the routes_by_store and the value is gonna be the full_path and store_aisle_items.
            #the store_aisles_items is all the aisles in order with there corresponding items in eahc aisle
            #full_path is the ordered coordniates of the route in a gird so I can use to display the route on a grid
            routes_by_store[str(store.name)] ={
                                            "aisles": store_aisle_items,   
                                            "path": full_path              
                                        }
            
        return routes_by_store

class orderDetail(View):
    #class that inherits from View WHere if computes the best route from a cart and creates a pastorder and redirects to pastorder that displays a single instance of a pastorder
    def post(self, request, cart_id):

        #grabs the current user and customer
        user = request.user
        customer = Customer.objects.get(user = user)
        #gets the current cart that the user is one that is passed on 
        cart = Cart.objects.get(pk = cart_id)

        #check if there are any items in the cart if not just redriect to cart like nothing happened
        if CartItem.objects.filter(cart = cart).count() >=1 :

            #set removed on the cart to be true so that the cartView doesnt display this cart anymore as an option as it is now a pastorder
            cart.removed = True
            #set the is_active to false as it is not longer active and this way there is aleays only one active cart at a time so the get int he cartView doesnt fail and somehow find more than one active cart
            cart.is_active = False

            #save the cart so changes apply 
            cart.save()
            #get all the cartItem obejcts that are asscoiated with this cart
            cartItems = CartItem.objects.filter(cart = cart)
            #inlize total price to be 0 
            total_price = 0 
            #inlize the string for all the items for a quick display of the items in the pastorder listview
            items = ""
            #inlize a list for all the items that the user wants to pass on to the best_route
            list_items = []
            for cartitem in cartItems:
                #iterate through all cartitem 

                #since cartitem has a foriegn key to an item I get the item and then get the price same for the name
                total_price += cartitem.item.price
                items += cartitem.item.name + "|"
                #add the item object to the list
                list_items.append(cartitem.item)

            # call best route to find the route for these items the start and end are default main and selfchekcout but the user can change the start from the map later
            routes = best_route(list_items , "Main" , "SelfCheckOut")

            #inlize a pastorder obejct with all the attributes I defined ealier
            pastOrder = PastOrder(customer= customer,
                                total_price = total_price,
                                items =items,
                                cart = cart,
                                #I am setting the routes as a dictonary with a key full and the route from best_route this is for telling if the user wants to split the route into diffrent routes 
                                #if there is only full in the dictonary as a key then it means that there is only one route to display but if splits is antoher key there will be muplte routes to display 
                                #but on creation there is only going to be one full route 
                                routes={"full": routes}
                                )
            
            # save the pastorder object
            pastOrder.save()
            
            
            # this is for when the user orders a cart it will remove that cart by setting removed to true but then I need to tell teh carView which cart to display next which will be the one that was updated last
            #if it fails it means there is not other carts so we do nothing
            #finds the current user and customer
            user = self.request.user
            customer = Customer.objects.get(user = user)
            try:
                
                #finds the last updated cart to set as active for display since we just remvoed the active one
                set_cart = Cart.objects.filter(customer = customer ,is_active = False,  removed = False).latest("updated_at")

                set_cart.is_active = True
                set_cart.save()
            except Cart.DoesNotExist:
                cart = None


            #This makes sure there is only a max of 10 pastorders int he database per customer
            orders = PastOrder.objects.filter(customer= customer).order_by("-timestamp")
            if orders.count() > 10 : 
                #finds the oldest orders but leaving 10 orders 
                delete_orders = orders[10:].values_list('id', flat=True)
                # deltes the orders 
                PastOrder.objects.filter(id__in=delete_orders).delete()


            




            return redirect('PastOrder' , pk=pastOrder.pk)
        
        else:
            
            return redirect('Cart')
    



class CreateCart(LoginRequiredMixin,CreateView):
    #a class that inherits form CreateView that interacts with the form CreateCartform to display it on the create_cart_form.html to create a new cart
    form_class = CreateCartForm
    template_name = "project/create_cart_form.html"


    def get_login_url(self) -> str:
        #redircets the use to the login page if they are not logged in already this is from LoginRequiredMixin
        '''return the URL required for login'''
        return reverse('Login') 
    


    def form_valid(self, form):
        '''This method handles the form submission and saves the 
        new object to the Django database.
        '''
        
		# instrument our code to display form fields: 
        print(f"CreateCommentView.form_valid: form.cleaned_data={form.cleaned_data}")

        #gets current user and customer
        user = self.request.user
        customer = Customer.objects.get(user = user)
        #tries to find an acitve cart of the user if there is one then set is to not active as the cart created will become the active one
        try:
            cart = Cart.objects.get(customer=customer, is_active=True)
            cart.is_active = False
            cart.save()
        except Cart.DoesNotExist:
            cart = None

        #attach the customer as a forgien key to the from for creating a cart 
        form.instance.customer = customer # set the FK


         # save the cart to database
        form.save()

        # delegate the work to the superclass method form_valid:
        return super().form_valid(form)

    def get_success_url(self):
        '''Provide a URL to redirect to after creating a new StatusMessage.'''

        # call reverse to generate the URL for this cart with the new active cart
        return reverse('Cart')
    




class DeleteCart(LoginRequiredMixin, DeleteView):

    #class that inhierts from the  Delete rendering the delete_cart_form html for the confermation page
    template_name = "project/delete_cart_form.html"
    model = Cart
    context_object_name = 'cart'


    def get_login_url(self) -> str:
            #redircets the use to the login page if they are not logged in already this is from LoginRequiredMixin
        '''return the URL required for login'''
        return reverse('login') 



    def get_success_url(self):
        '''Provide a URL to redirect to after updating the profile.'''

        #tries to find an acitve cart of the user if there is one then set it to  active as true as the cart delted is no longer active
        try:
            user = self.request.user
            customer = Customer.objects.get(user = user)
            set_cart = Cart.objects.filter(customer = customer ,is_active = False,  removed = False).latest("updated_at")

            set_cart.is_active = True
            set_cart.save()
        except Cart.DoesNotExist:
            cart = None
        return reverse('Cart')
    



class SinglePastOrder(DetailView):
    #class that inherits from detailview to display a single instance of a pastorder object
    model = PastOrder
    template_name = "project/single_past_order.html"
    context_object_name = 'order'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #gets this order object
        order = self.get_object()
        

        #define grid of star market to use in the javascirpt to display the map 
        grid = [[-1      ,-1                  ,-1 ,-1 ,-1                        ,-1       ,-1         ,-1         ,-1            ,-1              ,-1              ,-1         ,-1         ,-1                    ,-1        ,-1        ,-1        ,-1               ,-1         ,-1                  ,-1         ,-1         ,-1         ,-1                                 ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1],
           [-1      ,"Fish & Shellfish"  ,0 ,0 ,0                         ,0        ,0          ,0          ,0             ,0               ,0               ,0          ,0          ,"Meats"                ,0         ,0         ,0         ,0                ,0         ,"Lunch Meat"         ,0          ,0          ,0          ,"Prepared & Frozen Meat"          ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1],
           [-1      ,0                   ,0 ,0 ,0                         ,0        ,0          ,0          ,0             ,0               ,0               ,0          ,0          ,0                     ,0         ,0         ,0         ,0                ,0         ,0                    ,0          ,0          ,0          ,0                                  ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1],
           [-1      ,0                   ,0 ,"Deli",0                     ,-1       ,0          ,-1         ,0             ,-1              ,0               ,-1         ,0          ,-1                    ,0         ,-1        ,0         ,-1               ,0         ,-1                   ,0          ,-1         ,0          ,-1                                 ,0          ,-1         ,0          ,-1         ,0          ,0          ,"Dairy"    ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1],
           [-1      ,0                   ,0,0,0                          ,-1       ,"Aisle 1"        ,-1         ,0             ,-1              ,0               ,-1         ,0          ,-1                    ,0         ,-1        ,0         ,-1               ,0         ,-1                   ,0          ,-1         ,0          ,0                                  ,0          ,-1         ,0          ,-1         ,0          ,-1         ,0          ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1],
           [-1      ,0                   ,0,0 ,0                         ,0        ,0          ,"Aisle 2"        ,0             ,0               ,0               ,-1         ,0          ,-1                    ,0         ,-1        ,0         ,-1               ,0         ,-1                   ,0          ,-1         ,0          ,-1                                 ,0          ,-1         ,0          ,-1         ,0          ,0          ,0          ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1],
           [-1      ,"Prepared Specialty",0,0,0                          ,0        ,-1         ,0          ,-1            ,-1              ,"Aisle 3"             ,0          ,"Aisle 4"        ,0                     ,"Aisle 5"       ,0         ,"Aisle 6"       ,"Frozen"         ,"Aisle 7"         ,0                  ,"Aisle 8"         ,0         ,"Aisle 9"         ,0                                 ,"Aisle 10"       ,0         ,"Aisle 11"         ,0         ,"Aisle 12"       ,0         ,0           ,0          ,0          ,0          ,0          ,0          ,0          ,-1],
           [-1      ,0                   ,0,0,0                          ,0        ,-1         ,0          ,-1            ,-1              ,0               ,-1         ,0          ,-1                    ,0         ,-1        ,0         ,-1               ,0         ,-1                   ,0          ,-1         ,0          ,-1                                 ,0          ,-1         ,0          ,-1         ,0          ,-1         ,0          ,-1         ,0          ,-1         ,0          ,-1         ,0          ,-1],
           [-1      ,0                   ,0,0,0                          ,"Produce",-1         ,0          ,-1            ,-1              ,0               ,-1         ,0          ,-1                    ,0         ,-1        ,0         ,-1               ,0         ,-1                   ,0          ,-1         ,0          ,-1                                 ,0          ,-1         ,0          ,-1         ,0          ,-1         ,"Aisle 13"       ,0          ,"Aisle 14"       ,0          ,"Aisle 15"       ,-1         ,"Aisle 16"       ,-1],
           [-1      ,0                   ,0,"Nuts & Dried Fruits",0      ,0        ,-1         ,0          ,-1            ,-1              ,0               ,-1         ,0          ,-1                    ,0         ,-1        ,0         ,-1               ,0         ,-1                   ,0          ,-1         ,0          ,-1                                 ,0          ,0          ,0          ,-1         ,0          ,-1         ,0          ,-1         ,0          ,-1         ,0          ,-1         ,0          ,-1],
           ["Alchol",0                   ,0,"Fresh Fruits",0             ,0        ,0          ,0          ,0             ,0               ,0               ,0          ,0          ,0                     ,0         ,0         ,0         ,0                ,0         ,0                    ,0          ,0          ,0          ,0                                  ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,"Pharmacy"],
           [-1      ,"Bakery"            ,0,0,0                          ,0        ,0          ,0          ,"SelfCheckOut",0               ,0               ,0          ,0          ,0                     ,0         ,0         ,0         ,0                ,0         ,0                    ,0          ,0          ,0          ,0                                  ,0          ,0          ,0          ,"Flower"   ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,-1],
           ["Main"  ,0                   ,0,0,0                          ,0        ,0          ,0          ,0             ,0               ,0               ,0          ,0          ,0                     ,0         ,0         ,0         ,0                ,0         ,0                    ,0          ,0          ,0          ,0                                  ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,0          ,"Back"],
           [-1      ,-1                  ,-1,-1,-1                         ,-1       ,-1         ,-1         ,-1            ,-1              ,-1              ,-1         ,-1         ,-1                    ,-1        ,-1        ,-1        ,-1               ,-1         ,-1                  ,-1         ,-1         ,-1         ,-1                                 ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1         ,-1]]


        
        #set default value of the selected_route_name to be full then check if splits is in the dicotnary if it is that means we should pass the splited routes 
        context["selected_route_name"] = "full"
        context["selected_route"] = order.routes["full"]
        if "splits" in order.routes:
            #if there is splits set the default route to be displayed as route1 
            context["selected_route"] = order.routes["splits"]["route1"]
            context["selected_route_name"] = "route1"
            # check if user slected a diffrent route
            if 'selected_route' in self.request.GET:
                    selected_route = self.request.GET['selected_route']
                    if selected_route and selected_route != "full":
                        #passes the route that the user selected via the form in the html
                        context["selected_route_name"] = selected_route
                        context["selected_route"] = order.routes["splits"][selected_route]

        # gets all the stores in the route
        store_name = list(context["selected_route"].keys())[0]
        # gets all the aisles in the route based on the store as of right now I only have one store is I can just elave this as is 
        aisles = list(context["selected_route"][store_name]["aisles"].keys())
        path = list(context["selected_route"][store_name]["path"])

        context["layout"] = grid
        context["route"] = aisles
        context["path"] = path
        return context
    

    def post(self, request, *args, **kwargs):   
        # checks if the user make a request to switch the start of the route
        if request.path.endswith("switchstart/"):
            #get the current pastorder object
            order = self.get_object()
            #defaults to the full route if splits is not in routes
            selected_route  = order.routes["full"]
            #checks if splits in the routes if so it will find which route the user wants to switch the start from the url pass on by the form 
            if "splits" in order.routes:
                selected_route = order.routes["splits"]["route1"]
                if "selected_route" in request.GET:
                    selected_route_name = self.request.GET['selected_route']
                    if selected_route_name and selected_route_name != "full":
                        selected_route =  order.routes["splits"][request.GET["selected_route"]]

            # checks if the start input varable is in the url just a safty messure just incase somehow switchstart was passed but not start
            if 'start' in self.request.GET:
                # gets which start the user selcected right now there is only main and back for star market
                start= self.request.GET['start']
                if start:
                    
                        
                        #Finds all the items in this route which only sotre the names 
                        for store in selected_route.keys():
                            #print("store:" , store)
                            list_items = []
                            for aisle , items in selected_route[store]["aisles"].items(): 
                                    list_items.extend(items)

                        #print("items: ", list_items)
                        # find all items obejcts that mathc the names in the list from the asile of the selceted route
                        list_items = list(Item.objects.filter(name__in=list_items))
                        # call best_route to find best route for this list of items
                        routes = best_route(list_items , start , "SelfCheckOut")
                        #checks if splits is in route if it is replace the correct route with the new route with new start
                        #else replace the full route with route as it should be full route if there is not splits in the route as I remove it if the user deicded to split back to only 1 route and add if it they split into more routes 
                        if "splits" in order.routes and "selected_route" in request.GET:
                            if selected_route_name != "full":
                                order.routes["splits"][selected_route_name] = routes
                        else:
                            order.routes["full"] = routes

                        # save the changes in the object
                        order.save()
                        return redirect("PastOrder", pk=order.pk)
        
        return super().post(request, *args, **kwargs)





def backtracking(items, num_splits):

    return


def kk(items, num_splits):
    #this method takes all the items and finds the best split amount them based on number of splits to be as close as possible to equal price among all splits
    # this uses the bucket method

    #inlizes routes to have as many empty lists in the list as num_splits
    routes = routes = [[] for _ in range(num_splits)]
    #inlizes the total price of each splits as 0 
    total_price = [0]*num_splits
    #sorts all items from biggest price to smallest price
    sorted_items = sorted(items, key=lambda x: x.price, reverse=True)

    #goes through each item 
    for item in sorted_items: 
        #finds the index of the buck to place this item finds the buck/index of the smalles total price
        index = total_price.index(min(total_price))
        # addes the item to the bucket/index
        routes[index].append(item)
        # updates the total price of that bucket
        total_price[index]+= item.price

    #return the routes of the splits 
    return routes


def split_by_price(items , num_splits):
    #this method was intended to decide which type of method to use based on number of items and splits
    if len(items) <= 15 and num_splits <=4:
        #was going to implement backtracking if I had time as it is more accurate to find the optimal split for even pricing 
        return kk(items, num_splits)
       #return   backtracking(items, num_splits)
    else:
        #bucket method is less accurate but fast and great for large splits and items
        return kk(items, num_splits)
    

class SplitRouteView(View):
    # thsi class inhertis from View which does operations in order to split up the routes 

    def post(self, request, pk):
        #finds the pastorder object that was passed on 
        order = PastOrder.objects.get(pk = pk)

        #checks if the user requested a split or not
        if 'num_splits' in self.request.POST:
            #gets the input and convert it to int 
            num_splits = int(self.request.POST['num_splits'])
            #checks if num_splits is defined
            if num_splits :
                #checks if the number of splits request is 1 that means we need to check if splits is in the route dictonary if so delete so the pastOrder View will only display the full route which is for one person
                if num_splits == 1:
                    #pops out splits fromthe routes dictonary if there is one
                    order.routes.pop("splits", None)  
                    # saves the changes
                    order.save()
                    #redirct to pastorder no need to anymore operations as we always store the full route
                    return redirect("PastOrder", pk=order.pk)
                
                #gets all the CartItems that are associated with this pastoder 
                cart_items = CartItem.objects.filter(cart=order.cart)
                #inlize a empty list to store all the items 
                items = []
                #iterate through all cartitems 
                for cart_item in cart_items: 
                    #makes sure that we get everysingle item as it helps give the bucket algorithm more options to evenly disperse the items amoung the routes
                    for _ in range(cart_item.quantity):
                        #addes the item however many times the quantity it has on the cart 
                        items.append(cart_item.item)

                #call the split_by_price funciton to return the routes 
                split_routes = split_by_price(items, num_splits)

                #inlize empty dictonary to store all the routes based on price splits 
                ordered_routes = {}

                #defines diffrent routes numbered 1 to number of routes split and finds the best route for those items in that route split 
                for number , list_items in enumerate(split_routes):
                    ordered_routes[f"route{number+1}"] = best_route(list_items , "Main" , "SelfCheckOut")

                #save the new routes into splits to tell the pastoder view that there was a split requested so display these 
                order.routes["splits"] = ordered_routes
                order.save()

        
       
              
        return redirect("PastOrder", pk=order.pk)
    




class ReorderView(View):
    #this class inherits from View and creates a new cart based on a previous pastorder this way we dont change an existing cart changing the pastorder for that cart as well
    def post(self, request, *args, **kwargs):
        #get the id of the pastorder the user is on 
        id = kwargs.get("pk")
        #the the pastorder and current customer 
        pastOrder = PastOrder.objects.get(pk = id)
        customer = Customer.objects.get(user = request.user)

        #set all the carts for this customer to false as this new created cart is going to be the active cart
        Cart.objects.filter(customer=customer).update(is_active=False)

        # define/create a new cart with the same attributes as the pastorder cart
        new_cart = Cart.objects.create(name = pastOrder.cart.name , customer = customer)
        #find all the items of the pastorder cart 
        cartItems = CartItem.objects.filter(cart = pastOrder.cart)

        # iterate through all the pastorder cartItems
        for cartItem in cartItems:
            # create new CartITems to represent the relationship from item to the new created cart 
            cartItem = CartItem.objects.create(cart = new_cart, item= cartItem.item, quantity = cartItem.quantity)

        # redirect to cart to display the new cart that was reordered 
        return redirect("Cart")