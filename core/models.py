from django.db import models
from django.conf import settings
from djangotoolbox.fields import DictField
from singleton_models.models import SingletonModel

PRODUCT_IMAGES_DIR = 'product_images/'
SHIPPING_DEFAULT = 500

class BaseModel(models.Model):
    name = models.CharField(max_length=64, default='')
    created_at = models.DateTimeField(null=False, auto_now_add=True)
    modified_at = models.DateTimeField(null=False, auto_now=True)
    active = models.BooleanField(default=False)

    class Meta:
        abstract = True
    
    def extra_content(self):
        return None
    
    def table_header(self):
        output = '<thead>'
        for field in self._meta.fields:
            output += '<th>%s</th>' % field.name
        output += '</thead>'
        return output
    
    def as_table_row(self):
        output = '<tr>'
        for field in self._meta.fields:
            if field.name != 'id':
                output += '<td>%s</td>' % getattr(self, field.name)
            else:
                output += '<td><a href="/reports/generic_table/' + self.META().app_label + '/' + self.META().object_name + '/' + getattr(self, field.name) + '/">' 
                output += getattr(self, field.name) +'</a> </td>'
        output += '</tr>'
        return output
    
    def META(self):
        return self._meta
    
    def __unicode__(self):
        return self.name

class Category(BaseModel):
    display_name = models.CharField(max_length=64, default='')
    
    @property
    def image_url(self):
        from core.models import StoreItem
        items = StoreItem.objects.filter(category=self, active=True).order_by('priority')[:1]
        for item in items:
            return item.image_url
        return ''        
    
class StoreItem(BaseModel):
    display_name = models.CharField(max_length=64, default='')
    price_in_cents = models.IntegerField(null=False, default=200)
    image = models.ImageField(upload_to=PRODUCT_IMAGES_DIR)
    short_desc =  models.TextField(null=True, blank=True)
    long_desc =  models.TextField(null=True, blank=True)
    featured = models.BooleanField(default=False)
    category = models.ForeignKey(Category, null=True, blank=True)
    priority = models.IntegerField(null=False, default=999)
    
    @property
    def image_url(self):
        return self.image.url
    
    @property
    def price(self):
        return "{0:.2f}".format(float(self.price_in_cents)/100)
    
class Order(BaseModel):
    items = DictField(blank=True)
    price_in_cents = models.IntegerField(null=False, default=200)
    paid = models.BooleanField(default=False)
    shipping = models.IntegerField(null=True)
    ship_to = models.TextField(null=True, blank=True)
    email = models.CharField(max_length=200, default='')
    html_content = models.TextField(null=True, blank=True)

class HomePage(SingletonModel):
    html_content = models.TextField(null=True, blank=True)
    
class AboutPage(SingletonModel):
    html_content = models.TextField(null=True, blank=True)
    
class CSSFile(SingletonModel):
    css_content = models.TextField(null=True, blank=True)
    
class JSFile(SingletonModel):
    js_content = models.TextField(null=True, blank=True)
    
class AppSettings(SingletonModel):
    tax_percentage = models.IntegerField(null=False, default=7)
    shipping_on = models.BooleanField(default=False)
    send_to_mail_comma_separated_list = models.CharField(null=False, default='dan@blackbeltprogramming.com', max_length=1000)
    featured_section_on = models.BooleanField(default=True)
    featured_section_text = models.CharField(null=False, default='Featured', max_length=1000)
    category_section_on = models.BooleanField(default=True)
    categories_section_text = models.CharField(null=False, default='Categories', max_length=1000)
    make_my_cookies_header = models.CharField(null=False, 
        default='Traditions shouldn\'t fade. We\'ll help continue to provide your family with the cookies you\'ve had for generations.', max_length=1000)
    contact_us_header = models.CharField(null=False, default='If you have a question, comment, or suggestion we\'d love to hear it!', max_length=1000)
    
class PageTabName(SingletonModel):
    home =  models.CharField(null=False, default='Home', max_length=50)
    about =  models.CharField(null=False, default='About', max_length=50)
    make_my_cookies = models.CharField(null=False, default='Make My Cookies &trade;', max_length=50)
    bakery = models.CharField(null=False, default='Bakery', max_length=50)
    contact = models.CharField(null=False, default='Contact', max_length=50)
    
class ShippingOption(BaseModel):
    description = models.CharField(max_length=64, default='')
    price_in_cents = models.IntegerField(null=False, default=500)
    priority = models.IntegerField(null=False, default=999)
    
    @property
    def price(self):
        return "{0:.2f}".format(float(self.price_in_cents)/100)