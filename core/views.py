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
from django.core.mail import send_mail
from djrill.mail import DjrillMessage
import cloudfiles
from cloudfiles.errors import NoSuchContainer




def tabnames():
    d = {}
    d['home'] = PageTabName.instance(PageTabName).home
    d['about'] = PageTabName.instance(PageTabName).about
    d['make_my_cookies'] = PageTabName.instance(PageTabName).make_my_cookies
    d['bakery'] = PageTabName.instance(PageTabName).bakery
    d['contact'] = PageTabName.instance(PageTabName).contact
    return d

@render_to('robots.txt')
def robots(request):
    return {}    

@render_to('custom_file')
def custom_css(request):
    return {'content': CSSFile.instance(CSSFile).css_content , 'tabnames': tabnames()}

@render_to('custom_file')
def custom_js(request):
    return {'content': JSFile.instance(JSFile).js_content , 'tabnames': tabnames()}


@render_to('home.html')
def home(request):
    return {'tab':'home', 'home_content': HomePage.instance(HomePage).html_content , 'tabnames': tabnames()}

@render_to('terms.html')
def terms(request):
    return {'terms': AppSettings.instance(AppSettings).terms_and_conditions , 'tabnames': tabnames()}

@render_to('storefront.html')
def bakery(request):
    return {'tab':'bakery','featured':StoreItem.objects.filter(active=True, featured=True),
             'categories':Category.objects.filter(active=True),
             'featured_on': AppSettings.instance(AppSettings).featured_section_on,
             'category_on': AppSettings.instance(AppSettings).category_section_on,
             'featured_text': AppSettings.instance(AppSettings).featured_section_text,
             'category_text': AppSettings.instance(AppSettings).categories_section_text, 'tabnames': tabnames()}

@render_to('about.html')
def about(request):
    return {'tab':'about', 'about_content': AboutPage.instance(AboutPage).html_content , 'tabnames': tabnames()}

@render_to('contact.html')
def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        emailaddress = request.POST.get('email')
        phonenumber = request.POST.get('phonenumber')
        message = request.POST.get('message')
    
        if not emailaddress or not message:
            return{'tab':'contact', 'posted':True, 'success':False}
    
        subject = "You were contacted by " + emailaddress
        from_email = settings.DEFAULT_FROM_EMAIL
        from_name = "Anonymous" if not name else name # optional
        to = AppSettings.instance(AppSettings).send_to_mail_comma_separated_list.split(',')
        text_content = "Email address: " + emailaddress + "\nPhone Number: "+phonenumber+"\nName: "+name+"\nMessage: "+ message
        html_content = text_content
        msg = DjrillMessage(subject, text_content, from_email, to, tags=[], from_name=from_name)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return {'tab':'contact', 'posted':True, 'success':True, 'content': AppSettings.instance(AppSettings).contact_us_header , 'tabnames': tabnames()}
    return {'tab':'contact', 'content': AppSettings.instance(AppSettings).contact_us_header , 'tabnames': tabnames()}

@render_to('mmc.html')
def mmc(request):
    if request.method == "POST":
        name = request.POST.get('name')
        emailaddress = request.POST.get('email')
        phonenumber = request.POST.get('phonenumber','')
        instructions = request.POST.get('instructions','')
        text_recipe = request.POST.get('text_recipe','')
        num_of_files = int(request.POST.get('num_of_files',1))
    
        connection = cloudfiles.get_connection( settings.RACKSPACE_USERNAME,settings.RACKSPACE_APIKEY )
        try:
            bucket = connection.get_container( 'MMC' )
        except NoSuchContainer:
            bucket = connection.create_container( 'MMC' )
            
        if not bucket.is_public():
            bucket.make_public( 900 )
    
        if not emailaddress:
            return{'tab':'mmc', 'posted':True, 'success':False}
    
        subject = "Make my cookie request from " + emailaddress
        from_email = settings.DEFAULT_FROM_EMAIL
        from_name = "Anonymous" if not name else name # optional
        to = AppSettings.instance(AppSettings).send_to_mail_comma_separated_list.split(',')
        html_content = "Email address: " + emailaddress + "<br/>Phone Number: "+phonenumber+"<br/>Name: "+name+"<br/>Instructions: "+ instructions + "<br/>Text Recipe: " + text_recipe
        text_content = "Email address: " + emailaddress + "\nPhone Number: "+phonenumber+"\nName: "+name+"\nInstructions: "+ instructions + "\nText Recipe: " + text_recipe
        extra_text = ''
        extra_html = ''
        
        for iter in range(1,num_of_files+1):
            try:
                file  = request.FILES['file'+str(iter)]
                if file:
                    cloud_file = bucket.create_object(file.name)
                    for chunk in file.chunks():
                        cloud_file.write(chunk)
                    extra_text = extra_text + "\nUploaded File: " + cloud_file.public_uri()
                    extra_html = extra_html + '<br/><a href="' + cloud_file.public_uri() + '">' + file.name + '</a>'
            except:
                pass
        
        html_content = html_content + extra_html
        text_content = text_content + extra_text
        msg = DjrillMessage(subject, text_content, from_email, to, tags=[], from_name=from_name)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return {'tab':'mmc', 'posted':True, 'success':True, 'content':AppSettings.instance(AppSettings).make_my_cookies_header , 'tabnames': tabnames()}
    return {'tab':'mmc', 'content': AppSettings.instance(AppSettings).make_my_cookies_header , 'tabnames': tabnames()}

@render_to('checkout.html')
def checkout(request):
    tax_percentage = float(AppSettings.instance(AppSettings).tax_percentage)/100
    shipping_on = AppSettings.instance(AppSettings).shipping_on
    shipping_options = ShippingOption.objects.filter(active=True).order_by('priority')
    stripe.api_key = AppSettings.instance(AppSettings).stripe_api_key
    if request.method=='POST':
        email_text_body = ''
        purchased = {}
        saved_history = {}
        
        ship_price = ShippingOption.objects.get(id=request.POST.get('shipping')).price_in_cents if shipping_on else 0
        for key,value in request.POST.items():
            m = re.match(r'^id_(.*)', key)
            if m:
                store_item = StoreItem.objects.get(id=m.group(1))
                purchased[store_item] = int(value)
                email_text_body = email_text_body + value + ' ' + store_item.display_name + ' each for $' + store_item.price + "\n"
                saved_history[store_item.id] = {
                    'item_name': store_item.display_name,
                    'item_price': store_item.price,
                    'quantity' : int(value)
                }
        price = 0
        for key,value in purchased.items():
            price = key.price_in_cents * value + price
        
        email_text_body = email_text_body + "Subtotal: $" + '{:20,.2f}'.format(float(price / 100)) + '\n'
        email_text_body = email_text_body + "Tax: $" + '{:20,.2f}'.format(float(int(math.ceil(price *tax_percentage)) / 100) ) + '\n'
        if ship_price > 0:
            email_text_body = email_text_body + "Shipping: $" + '{:20,.2f}'.format(float(ship_price / 100)) + '\n'
        
        
        price = int(math.ceil(price * (1 + tax_percentage))) + ship_price
        
        email_text_body = email_text_body + "Total: $" + '{:20,.2f}'.format(float(price / 100)) + '\n'
        
        eship_to = request.POST.get('email')
        if not eship_to:
            return {'tab':'bakery', 'cart':request.session.get('cart'), 'error':True, 'tax':tax_percentage, 'shipping_on':shipping_on, 'shipping_options':shipping_options}
        ship_to = "Name: " + request.POST.get('shipname', '') + "\n"
        ship_to = ship_to + "Address Line 1: " + request.POST.get('add1', '') + "\n"
        ship_to = ship_to + "Address line 2: " + request.POST.get('add2', '') + "\n"
        ship_to = ship_to + "City: " + request.POST.get('city', '') + "\n"
        ship_to = ship_to + "State: " + request.POST.get('state', '') + "\n"
        ship_to = ship_to + "Zip: " + request.POST.get('zip', '') + "\n"
        
        order = Order()
        order.items = saved_history
        order.price_in_cents = price
        order.email = eship_to
        order.ship_to = ship_to
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
                return {'tab':'bakery', 'cart':request.session.get('cart'), 'error':True, 'tax':tax_percentage, 'shipping_on':shipping_on, 'shipping_options':shipping_options, 'tabnames': tabnames()}
        except Exception as stripe_error:
            request.session['cart'] = purchased
            return {'tab':'bakery', 'cart':request.session.get('cart'), 'error':True, 'tax':tax_percentage, 'shipping_on':shipping_on, 'shipping_options':shipping_options, 'tabnames': tabnames()}
        
        order.paid=True
        order.save()
        request.session['cart'] = {}
        
        subject = "Biscotti Plus Order Confirmation "
        from_email = settings.DEFAULT_FROM_EMAIL
        from_name = "Biscotti Plus"
        to = [order.email]
        text_content = "Your order has been placed. This email is your receipt.\n"
        text_content = text_content + email_text_body + "\nShipping info:\n" + ship_to
        html_content = "Your order has been placed. This email is your receipt.<br/>"
        html_content = html_content + email_text_body.replace('\n','<br/>') + "<br/>Shipping info:<br/>" + ship_to.replace('\n','<br/>')
        msg = DjrillMessage(subject, text_content, from_email, to, tags=[], from_name=from_name)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
        order.html_content = html_content
        order.save()
        
        subject2 = 'An order has been placed at Bisco by ' + order.email
        text_content = "The following has been paid for. Below is the reciept sent to " + order.email + "\n " + text_content
        html_content = "The following has been paid for. Below is the reciept sent to " + order.email + "<br/> " + html_content
        to2 = AppSettings.instance(AppSettings).send_to_mail_comma_separated_list.split(',')
        msg2 = DjrillMessage(subject2, text_content, from_email, to2, tags=[], from_name=from_name)
        msg2.attach_alternative(html_content, "text/html")
        msg2.send()
        
        
        
        return HttpResponseRedirect(reverse('order_confirmed', args=(order.id,)))
            
    return {'tab':'bakery', 'cart':request.session.get('cart'), 'tax':tax_percentage, 'shipping_on':shipping_on, 'shipping_options':shipping_options , 'tabnames': tabnames()}

@render_to('category.html')
def category(request,id):
    category = Category.objects.get(id=id)
    return{'tab':'bakery','category':category, 'items':StoreItem.objects.filter(active=True,category=category).order_by('priority'), 'tabnames': tabnames()}
    
@render_to('item.html')
def item(request,id):
    return{'tab':'bakery','item':StoreItem.objects.get(id=id), 'tabnames': tabnames()}
    
@render_to('order.html')
def order_confirmed(request,id):
    return {'order':Order.objects.get(id=id), 'tabnames': tabnames()}
    
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
    if cart:
        return {'success':True, 'empty':False }
    return {'success':True, 'empty':True }

@jsonify
def foward(request):
    subject = "Direct Mail Forwarded "
    from_email = settings.DEFAULT_FROM_EMAIL
    from_name = "Anonymous" if not name else name # optional
    to = AppSettings.instance(AppSettings).send_to_mail_comma_separated_list.split(',')
    text_content = request.POST
    html_content = text_content
    msg = DjrillMessage(subject, text_content, from_email, to, tags=[], from_name=from_name)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    return {'success':True}