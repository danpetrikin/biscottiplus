from django.contrib import admin
from models import *

from singleton_models.admin import SingletonModelAdmin
        
admin.site.register(AppSettings, SingletonModelAdmin)
admin.site.register(HomePage, SingletonModelAdmin)
admin.site.register(AboutPage, SingletonModelAdmin)
admin.site.register(CSSFile, SingletonModelAdmin)
admin.site.register(JSFile, SingletonModelAdmin)

admin.site.register(StoreItem)
admin.site.register(Category)
admin.site.register(ShippingOption)
admin.site.register(PageTabName)
admin.site.register(CustomPicture)