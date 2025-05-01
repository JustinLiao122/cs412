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

import math



class Welcome(TemplateView):
    template_name = "project/welcome.html"






class CreateCustomerView(CreateView):

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
    model = Item
    template_name = "project/item.html"
    content_object_name = "item"
    

class Shop(ListView):
    model = Item
    template_name = "project/shop.html"
    context_object_name = "items"
    paginate_by = 50


    def get_queryset(self):
        # THis method is used to query the database and filter the items based on the submisson of the form in the url
            
        results = super().get_queryset()
        name = self.request.GET.get('q')
        if name:
            try:
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
                hits = response["hits"]["hits"]

                if hits:
                    ids = [hit["_id"] for hit in hits]
                    return Item.objects.filter(id__in=ids)
                else:
                    print("Using default Search")
                    return results.filter(name__icontains=name)

            except Exception as e:
                print(f"Error connecting to Elasticsearch: {e}")
                print("Using default Search")
                return results.filter(name__icontains=name)
        
        return results



class ActiveCartDetailView(TemplateView):
    template_name = "project/cart.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        customer = Customer.objects.get(user = user)

        try:
            cart = Cart.objects.get(customer=customer, is_active=True)
        except Cart.DoesNotExist:
            cart = None

       

        context['cart'] = cart
        context['cart_items'] = CartItem.objects.filter(cart=cart)
        context['inactive_carts'] = Cart.objects.filter(customer=customer, is_active=False, removed = False)

        return context

def switch_to_cart(request, cart_id):
    cart = Cart.objects.get(pk = cart_id)
    customer = cart.customer

    Cart.objects.filter(customer=customer).update(is_active=False)

    cart.is_active = True
    cart.save()

    return redirect('Cart')  


def remove_from_cart(request, item_id, cart_id):
    cart = Cart.objects.get(pk = cart_id)
    item = Item.objects.get(pk = item_id)
    print("Cart ID:", cart.id)
    print("Item ID:", item.id)
    cartitem = CartItem.objects.get(cart = cart , item = item )
    if cartitem:
        cartitem.delete()
    return redirect('Cart')







def AddToCartView(request, item_id):
    item = Item.objects.get(pk = item_id)
    user = request.user
    customer = Customer.objects.get(user = user)
    cart = Cart.objects.get(customer = customer, is_active=True)

    cartitem, created = CartItem.objects.get_or_create(cart=cart, item=item)
    if not created:
        cartitem.quantity += 1
        cartitem.save()

    
    return HttpResponse(status=204)


class PastOrders(ListView):

    model = PastOrder
    template_name = "project/past_order.html"
    context_object_name = "past_order"
    paginate_by = 50


    def get_queryset(self):
        # THis method is used to query the database and filter the items based on the submisson of the form in the url
            
        results = super().get_queryset()
        results = results.order_by("-timestamp")
       
        
        return results



class RenameCartView(LoginRequiredMixin, UpdateView):
    model = Cart
    form_class = RenameCartForm
    template_name = "project/rename_cart_form.html"
    context_object_name = "cart"


    def get_success_url(self):
        return reverse('Cart') 



def euclidean(coord1, coord2):
    return math.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)

def optimize_path(layout, aisle_list):
    current = layout["Main"]
    print("layout: " , layout)
    aisles_to_visit = aisle_list.copy()
    ordered_aisles = []

    while aisles_to_visit:
        # Find closest aisle
        next_aisle = min(aisles_to_visit, key=lambda aisle: euclidean(current, layout[aisle]))
        ordered_aisles.append(next_aisle)
        current = layout[next_aisle]
        aisles_to_visit.remove(next_aisle)

    return ordered_aisles



def best_route( items, start, end ):
        store_aisles = {}
        store_items = {}
        for item in items:
            store = item.store
            aisle = item.aisle

            if store not in store_aisles:
                store_aisles[store] = []

            if aisle not in store_aisles[store]:
                store_aisles[store].append(aisle)

            if store not in store_items:
                store_items[store] = {}
            if aisle not in store_items[store]:
                store_items[store][aisle] = []
            store_items[store][aisle].append(item.name)



        routes_by_store = {}
        for store, aisle_to_visit in store_aisles.items():
            store_aisle_items = {}
            if len(aisle_to_visit) <= 15: 
                route = store.A_star_method( aisle_to_visit, start, end )
            else:
                #going to use cluster routeing less optimal but way faster for greater number of aisle
                #will implment later down the line if I include other stores besides star market as star only has 20 total aisle and dont think users will be needing to vissit all 20 for now
                route = store.A_star_method( aisle_to_visit, start, end )
            full_path = []

            for i in range(len(route) - 1):
                start_aisle = route[i]
                end_aisle = route[i + 1]

                aisle_distances = store.aisle_distances
                path_info = aisle_distances[start_aisle][end_aisle]

                if i == 0:
                    full_path.extend(path_info["path"])  
                else:
                    full_path.extend(path_info["path"][1:]) 

            for aisle in route: 
                if aisle == start or aisle == end: 
                    store_aisle_items[aisle] = []
                else:
                    store_aisle_items[aisle] = store_items[store][aisle]
            routes_by_store[str(store.name)] ={
                                            "aisles": store_aisle_items,   
                                            "path": full_path              
                                        }
            
        return routes_by_store

class orderDetail(View):

    def post(self, request, cart_id):
        user = request.user
        customer = Customer.objects.get(user = user)
        cart = Cart.objects.get(pk = cart_id)

        if CartItem.objects.filter(cart = cart).count() >=1 :
            cart.removed = True
            cart.is_active = False
            cart.save()
            cartItems = CartItem.objects.filter(cart = cart)
            total_price = 0 
            items = ""
            list_items = []
            for item in cartItems:
                total_price += item.item.price
                items += item.item.name + "|"
                list_items.append(item.item)
            routes = best_route(list_items , "Main" , "SelfCheckOut")

            pastOrder = PastOrder(customer= customer,
                                total_price = total_price,
                                items =items,
                                cart = cart,
                                routes={"full": routes}
                                )
            
            pastOrder.save()
            
            
                
            try:
                user = self.request.user
                customer = Customer.objects.get(user = user)
                set_cart = Cart.objects.filter(customer = customer ,is_active = False,  removed = False).latest("updated_at")

                set_cart.is_active = True
                set_cart.save()
            except Cart.DoesNotExist:
                cart = None



            orders = PastOrder.objects.order_by("-timestamp")
            if orders.count() > 10 : 

                delete_orders = orders[10:].values_list('id', flat=True)
                PastOrder.objects.filter(id__in=delete_orders).delete()


            




            return redirect('PastOrder' , pk=pastOrder.pk)
        
        else:
            
            return redirect('Cart')
    



class CreateCart(LoginRequiredMixin,CreateView):

    form_class = CreateCartForm
    template_name = "project/create_cart_form.html"


    def get_login_url(self) -> str:
        #redircets the use to the login page if they are not logged in already this is from LoginRequiredMixin
        '''return the URL required for login'''
        return reverse('Login') 
    


    def form_valid(self, form):
        '''This method handles the form submission and saves the 
        new object to the Django database.
        We need to add the foreign key (of the Article) to the Comment
        object before saving it to the database.
        '''
        
		# instrument our code to display form fields: 
        print(f"CreateCommentView.form_valid: form.cleaned_data={form.cleaned_data}")


        user = self.request.user
        customer = Customer.objects.get(user = user)
        try:
            cart = Cart.objects.get(customer=customer, is_active=True)
            cart.is_active = False
            cart.save()
        except Cart.DoesNotExist:
            cart = None

        #retrive the profile from get_object
        
        # attach this profile to the comment
        form.instance.customer = customer # set the FK


         # save the status message to database
        form.save()

       
        # read the file from the form:
    
        



        # delegate the work to the superclass method form_valid:
        return super().form_valid(form)

    def get_success_url(self):
        '''Provide a URL to redirect to after creating a new StatusMessage.'''

        # call reverse to generate the URL for this Profile with new message
        return reverse('Cart')
    




class DeleteCart(LoginRequiredMixin, DeleteView):

    #class that inhierts from the  Delete rendering the delete_status_form html for the confermation page
    template_name = "project/delete_cart_form.html"
    model = Cart
    context_object_name = 'cart'


    def get_login_url(self) -> str:
            #redircets the use to the login page if they are not logged in already this is from LoginRequiredMixin
        '''return the URL required for login'''
        return reverse('login') 



    def get_success_url(self):
        '''Provide a URL to redirect to after updating the profile.'''

        # create and return a URL:
        # retrieve the PK from the URL pattern
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
    routes = routes = [[] for _ in range(num_splits)]
    total_price = [0]*num_splits
    sorted_items = sorted(items, key=lambda x: x.price, reverse=True)

    for item in sorted_items: 
        index = total_price.index(min(total_price))
        routes[index].append(item)
        total_price[index]+= item.price

    return routes

def split_by_price(items , num_splits):
    if len(items) <= 15 and num_splits <=4:
        return kk(items, num_splits)
       #return   backtracking(items, num_splits)
    else:
        return kk(items, num_splits)
    

    




class SplitRouteView(View):

    def post(self, request, pk):
        order = PastOrder.objects.get(pk = pk)
        if 'num_splits' in self.request.POST:
            num_splits = int(self.request.POST['num_splits'])
            if num_splits :

                if num_splits == 1:
                    order.routes.pop("splits", None)  
                    order.save()
                    return redirect("PastOrder", pk=order.pk)
                cart_items = CartItem.objects.filter(cart=order.cart)
                items = []
                for cart_item in cart_items: 
                    for _ in range(cart_item.quantity):
                        items.append(cart_item.item)

                split_routes = split_by_price(items, num_splits)

                ordered_routes = {}

                for number , list_items in enumerate(split_routes):
                    ordered_routes[f"route{number+1}"] = best_route(list_items , "Main" , "SelfCheckOut")


                order.routes["splits"] = ordered_routes
                order.save()

        
       
              
        return redirect("PastOrder", pk=order.pk)