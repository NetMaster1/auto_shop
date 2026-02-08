from django.contrib import admin
from . models import AutoBrand, AutoModel, AutoModification, SDEK_Office, SDEK_City

class AutoBrandAdmin(admin.ModelAdmin):
    list_display = ('ozon_attribute_id', 'ozon_attribute_value',)
    search_fields = ('ozon_attribute_id', 'ozon_attribute_value' )
    list_per_page=100

class AutoModelAdmin(admin.ModelAdmin):
    list_display = ('ozon_attribute_id', 'ozon_attribute_value', 'ozon_attribute_info')
    search_fields = ('ozon_attribute_id', 'ozon_attribute_value', 'ozon_attribute_info' )
    ordering = ('-ozon_attribute_value',)
    list_per_page=200

class AutoModificationAdmin(admin.ModelAdmin):
    list_display = ('ozon_attribute_id', 'ozon_attribute_value', 'ozon_attribute_info')
    search_fields = ('ozon_attribute_id', 'ozon_attribute_value', 'ozon_attribute_info' )
    ordering = ('-ozon_attribute_value',)
    list_per_page=200
    
# ==========================================Sdek=========

class SDEK_OfficeAdmin(admin.ModelAdmin):
    list_display = ('country_code', 'code', 'type', 'address_full', 'city', 'city_code', 'region')
    search_fields = ('address_full', 'country_code', 'city', 'code', 'country_code', 'region')
    ordering = ('-address_full',)
    list_per_page=100

class SDEK_CityAdmin(admin.ModelAdmin):
    list_display = ('country_code', 'region', 'code', 'name',)
    search_fields = ('name', 'region', 'code')
    ordering = ('name',)
    list_per_page=100



admin.site.register(AutoBrand, AutoBrandAdmin)
admin.site.register(AutoModel, AutoModelAdmin)
admin.site.register(AutoModification, AutoModificationAdmin)
admin.site.register(SDEK_Office, SDEK_OfficeAdmin)
admin.site.register(SDEK_City, SDEK_CityAdmin)