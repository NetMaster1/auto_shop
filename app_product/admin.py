from django.contrib import admin
from . models import Product, DocumentType, RemainderHistory

class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'article', 'ozon_id', 'quantity', 'av_price', 'total_sum' )
    search_fields = ('article', )

class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',  )

class RemainderHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'rho_type', 'article', 'name', 'status', 'shipment_id', 'pre_remainder', 'incoming_quantity', 'outgoing_quantity', 'current_remainder')
    search_fields = ('article', )

admin.site.register(Product, ProductAdmin)
admin.site.register(DocumentType, DocumentTypeAdmin)
admin.site.register(RemainderHistory, RemainderHistoryAdmin)




