from django.contrib import admin
from .models import Route

# Register your models here.
# admin.site.register(Route)


from django.contrib.gis.admin import OSMGeoAdmin

@admin.register(Route)
class ShopAdmin(OSMGeoAdmin):
    list_display = ('user', 'date_and_time', 'start_point', 'finish_point')
