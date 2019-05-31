from django.contrib import admin

# Register your models here.
from proxy.models import UseNotify, BuyNotify

# Register your models here.

admin.site.register(UseNotify)
admin.site.register(BuyNotify)
