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
    
class AppSettings(SingletonModel):
    tax_percentage = models.IntegerField(null=False, default=7)
    shipping_on = models.BooleanField(default=False)
    
class ShippingOption(BaseModel):
    description = models.CharField(max_length=64, default='')
    price_in_cents = models.IntegerField(null=False, default=500)
    priority = models.IntegerField(null=False, default=999)
    
    @property
    def price(self):
        return "{0:.2f}".format(float(self.price_in_cents)/100)