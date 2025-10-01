from django.contrib import admin
from . models import AutoBrand, AutoModel, AutoModification

class AutoBrandAdmin(admin.ModelAdmin):
    list_display = ('ozon_attribute_id', 'ozon_attribute_value',)
    search_fields = ('ozon_attribute_id', 'ozon_attribute_value' )
    list_per_page=100


admin.site.register(AutoBrand, AutoBrandAdmin)