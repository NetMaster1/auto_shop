from django.contrib import admin
from . models import Product, DocumentType, Document, RemainderHistory, ProductCategory

class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'article', 'wb_true', 'ozon_true', 'site_true', 'update_true', 'image_1', 'image_2', 'image_3', 'ozon_id', 'ozon_sku', 'wb_id', 'wb_bar_code', 'length', 'width', 'height', 'quantity', 'manufacturer', 'av_price', 'total_sum', )
    search_fields = ('article', 'ozon_id', 'ozon_sku', 'wb_id', 'wb_bar_code' )
    list_editable = ('category', 'length', 'width', 'height', 'image_1', 'image_2', 'image_3', 'update_true', 'wb_true', 'ozon_true', 'site_true', 'quantity', 'total_sum', 'manufacturer')
    list_per_page=25

class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)

class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',  )

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'time_seconds')
    #I don't know how it works, but this functions created a separate column based on column 'created', but with more precise time '19 Feb 2022 15:54:00' instead of  'Feb. 21, 2022, 3:11 p.m.' I deleted 'created' from display_list. Somehow it may influence to filtering, but so far I have not noticed anything.
    def time_seconds(self, obj):
        return obj.created.strftime("%d %b %Y %H:%M:%S.%f")#displays microsecs
        #return obj.created.strftime("%d %b %Y %H:%M:%S")
    time_seconds.admin_order_field = 'created'
    time_seconds.short_description = 'Precise Time'

class RemainderHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'time_seconds', 'rho_type', 'article', 'name', 'status', 'shipment_id', 'pre_remainder', 'incoming_quantity', 'outgoing_quantity', 'current_remainder')
    search_fields = ('article', 'ozon_id', 'ozon_sku')
    list_editable = ('pre_remainder', 'incoming_quantity', 'outgoing_quantity', 'current_remainder',)
    list_per_page=50
    ordering = ('-created',)

    #I don't know how it works, but this functions created a separate column based on column 'created', but with more precise time '19 Feb 2022 15:54:00' instead of  'Feb. 21, 2022, 3:11 p.m.' I deleted 'created' from display_list. Somehow it may influence to filtering, but so far I have not noticed anything.
    def time_seconds(self, obj):
        return obj.created.strftime("%d %b %Y %H:%M:%S.%f")#displays microsecs
        #return obj.created.strftime("%d %b %Y %H:%M:%S")
    time_seconds.admin_order_field = 'created'
    time_seconds.short_description = 'Precise Time'

admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(DocumentType, DocumentTypeAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(RemainderHistory, RemainderHistoryAdmin)




