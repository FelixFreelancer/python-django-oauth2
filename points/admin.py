from django.contrib import admin
from points.models import Point

# Register your models here.
admin.site.site_header = 'AsiaTop Restful API Administrator'

admin.site.register(Point)
