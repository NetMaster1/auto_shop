from django.contrib import admin
from . models import Product, DocumentType, RemainderHistory, ProductCategory

class ProductAdmin(admin.ModelAdmin):
    list_display = ('id','category', 'name', 'article', 'ozon_id', 'ozon_sku', 'wb_id', 'length', 'width', 'quantity', 'av_price', 'total_sum', )
    search_fields = ('article', 'ozon_id', 'ozon_sku', 'wb_id' )
    list_editable = ('category', 'length', 'width', )

class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)

class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',  )

class RemainderHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'rho_type', 'article', 'name', 'status', 'shipment_id', 'pre_remainder', 'incoming_quantity', 'outgoing_quantity', 'current_remainder')
    search_fields = ('article', 'ozon_id', 'ozon_sku')

admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(DocumentType, DocumentTypeAdmin)
admin.site.register(RemainderHistory, RemainderHistoryAdmin)




