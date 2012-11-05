from django.contrib import admin
from models import *

from singleton_models.admin import SingletonModelAdmin
        
admin.site.register(AppSettings, SingletonModelAdmin)

admin.site.register(StoreItem)
admin.site.register(Category)
admin.site.register(ShippingOption)