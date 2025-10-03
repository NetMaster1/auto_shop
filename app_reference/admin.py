from django.contrib import admin
from . models import AutoBrand, AutoModel, AutoModification

class AutoBrandAdmin(admin.ModelAdmin):
    list_display = ('ozon_attribute_id', 'ozon_attribute_value',)
    search_fields = ('ozon_attribute_id', 'ozon_attribute_value' )
    list_per_page=100

class AutoModelAdmin(admin.ModelAdmin):
    list_display = ('ozon_attribute_id', 'ozon_attribute_value', 'ozon_attribute_info')
    search_fields = ('ozon_attribute_id', 'ozon_attribute_value', 'ozon_attribute_info' )
    ordering = ('-ozon_attribute_value',)
    list_per_page=200




admin.site.register(AutoBrand, AutoBrandAdmin)
admin.site.register(AutoModel, AutoModelAdmin)