from django.shortcuts import render

# Create your views here.
from django.shortcuts import redirect
from django.urls import reverse

from .models import*
from django.views.generic import ListView , DetailView ,CreateView ,UpdateView,DeleteView , View, TemplateView 
from .forms import* 
from django.contrib.auth.mixins import LoginRequiredMixin 
import math

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
            results = results.filter(name__icontains=name)
        
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


class PastOrders(ListView):

    model = PastOrder
    template_name = "project/past_order.html"
    context_object_name = "past_order"
    paginate_by = 50


    def get_queryset(self):
        # THis method is used to query the database and filter the items based on the submisson of the form in the url
            
        results = super().get_queryset()
        results.order_by("timestamp")
       
        
        return results





class AddToCartView(View):


    def post(self, request, item_id):
        item = Item.objects.get(pk = item_id)
        user = request.user
        customer = Customer.objects.get(user = user)
        cart = Cart.objects.get(customer = customer, is_active=True)

        cartitem, created = CartItem.objects.get_or_create(cart=cart, item=item)
        if not created:
            cartitem.quantity += 1
            cartitem.save()

        
        return  redirect(reverse('shop'))



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
            for aisle in route: 
                store_aisle_items[aisle] = store_items[store][aisle]
            routes_by_store[str(store)] = store_aisle_items
            
        return routes_by_store
class orderDetail(View):

    def post(self, request, cart_id):
        user = request.user
        customer = Customer.objects.get(user = user)
        cart = Cart.objects.get(pk = cart_id)
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
        routes = best_route(list_items , "Main" , "SelfCheckout")

        pastOrder = PastOrder(customer= customer,
                             total_price = total_price,
                              items =items,
                              cart = cart,
                             routes=routes
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




        return redirect('PastOrder' , pk=pastOrder.pk)
    



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
        order = self.get_object()
        cart_items = CartItem.objects.filter(cart=order.cart)

        items_by_aisle = {}
        for cart_item in cart_items:
            aisle = cart_item.item.aisle
            if aisle not in items_by_aisle:
                items_by_aisle[aisle] = []
            items_by_aisle[aisle].append(cart_item.item)

        context["items_by_aisle"] = items_by_aisle

        return context