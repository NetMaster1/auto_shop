from django.contrib import admin
from . models import Product, DocumentType, Document, RemainderHistory, ProductCategory

class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'article', 'wb_true', 'ozon_true', 'image_1', 'image_2', 'image_3', 'ozon_id', 'ozon_sku', 'wb_id', 'wb_bar_code', 'length', 'width', 'height', 'quantity', 'av_price', 'total_sum', )
    search_fields = ('article', 'ozon_id', 'ozon_sku', 'wb_id', 'wb_bar_code' )
    list_editable = ('category', 'length', 'width', 'height', 'image_1', 'image_2', 'image_3', 'wb_true', 'ozon_true' )
    list_per_page=25

class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)

class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',  )

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created')

class RemainderHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'rho_type', 'article', 'name', 'status', 'shipment_id', 'pre_remainder', 'incoming_quantity', 'outgoing_quantity', 'current_remainder')
    search_fields = ('article', 'ozon_id', 'ozon_sku')
    list_editable = ('current_remainder',)

admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(DocumentType, DocumentTypeAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(RemainderHistory, RemainderHistoryAdmin)




