from django.shortcuts import render

# Create your views here.
from django.shortcuts import redirect
from django.urls import reverse

from .models import*
from django.views.generic import ListView , DetailView ,CreateView ,UpdateView,DeleteView , View, TemplateView


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

        cart = Cart.objects.get(customer=customer, is_active=True)

        if not cart:
            cart = Cart.objects.create(customer=customer, is_active=True)

        context['cart'] = cart
        context['cart_items'] = CartItem.objects.filter(cart=cart)
        context['inactive_carts'] = Cart.objects.filter(customer=customer, is_active=False).exclude(id=cart.id)

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
