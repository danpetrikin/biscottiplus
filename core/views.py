# Create your views here.
from annoying.decorators import render_to
from core.decorators import jsonify
from core.models import *
import stripe
import re
from django.conf import settings
import math
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse

stripe.api_key = settings.STRIPE_API_KEY

@render_to('home.html')
def home(request):
    return {'tab':'home'}

@render_to('storefront.html')
def bakery(request):
    return {'tab':'bakery','featured':StoreItem.objects.filter(active=True, featured=True), 'categories':Category.objects.filter(active=True)}

@render_to('about.html')
def about(request):
    return {'tab':'about'}

@render_to('contact.html')
def contact(request):
    return {'tab':'contact'}

@render_to('mmc.html')
def mmc(request):
    return {'tab':'mmc'}

@render_to('checkout.html')
def checkout(request):
    tax_percentage = float(AppSettings.instance(AppSettings).tax_percentage)/100
    shipping_on = AppSettings.instance(AppSettings).shipping_on
    shipping_options = ShippingOption.objects.filter(active=True).order_by('priority')
    if request.method=='POST':
        purchased = {}
        saved_history = {}
        
        ship_price = ShippingOption.objects.get(id=request.POST.get('shipping')).price_in_cents if shipping_on else 0
        for key,value in request.POST.items():
            m = re.match(r'^id_(.*)', key)
            if m:
                store_item = StoreItem.objects.get(id=m.group(1))
                purchased[store_item] = int(value)
                saved_history[store_item.id] = {
                    'item_name': store_item.display_name,
                    'item_price': store_item.price,
                    'quantity' : int(value)
                }
        price = 0
        for key,value in purchased.items():
            price = key.price_in_cents * value + price
        price = int(math.ceil(price * (1 + tax_percentage))) + ship_price
        
        order = Order()
        order.items = saved_history
        order.price_in_cents = price
        order.save()
        
        try:
            stripe_token = None
            stripe_token = stripe.Token.create(
               card={
                 "number": request.POST.get('cardno'),
                 "exp_month": request.POST.get('month'),
                 "exp_year": request.POST.get('year'),
                 "cvc": request.POST.get('cvv')
               },
             ).id
    
            stripe_charge = stripe.Charge.create(
               amount=price,
               currency="usd",
               card=stripe_token,
               description="Charge for order #"+order.id
             )
    
            if not stripe_charge.paid:
                request.session['cart'] = purchased
                return {'tab':'bakery', 'cart':request.session.get('cart'), 'error':True, 'tax':tax_percentage, 'shipping_on':shipping_on, 'shipping_options':shipping_options}
        except Exception as stripe_error:
            print stripe_error
            request.session['cart'] = purchased
            return {'tab':'bakery', 'cart':request.session.get('cart'), 'error':True, 'tax':tax_percentage, 'shipping_on':shipping_on, 'shipping_options':shipping_options}
        
        order.paid=True
        order.save()
        request.session['cart'] = {}
        return HttpResponseRedirect(reverse('order_confirmed', args=(order.id,)))
            
    return {'tab':'bakery', 'cart':request.session.get('cart'), 'tax':tax_percentage, 'shipping_on':shipping_on, 'shipping_options':shipping_options}

@render_to('category.html')
def category(request,id):
    category = Category.objects.get(id=id)
    return{'tab':'bakery','category':category, 'items':StoreItem.objects.filter(active=True,category=category).order_by('priority')}
    
@render_to('item.html')
def item(request,id):
    return{'tab':'bakery','item':StoreItem.objects.get(id=id)}
    
@render_to('order.html')
def order_confirmed(request,id):
    return {'order':Order.objects.get(id=id)}
    
@jsonify
def item_to_cart(request,id):
    cart = request.session.get('cart',{})
    item = StoreItem.objects.get(id=id)
    if item in cart:
        cart[item] = cart[item]+1
    else:
        cart[item] = 1
    request.session['cart'] = cart
    return {'success':True}

@jsonify
def remove_item_from_cart(request,id):
    cart = request.session.get('cart',{})
    item = StoreItem.objects.get(id=id)
    if item in cart:
        del cart[item]
    request.session['cart'] = cart
    return {'success':True}