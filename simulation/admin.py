from django.contrib import admin
from simulation.models import Simulation
from simulation.models import Cnonce
# Register your models here.
admin.site.register(Simulation)
admin.site.register(Cnonce)
