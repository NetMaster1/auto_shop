from django.contrib import admin
from . models import DeliveryOperator

class DeliveryOperatorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', )


admin.site.register(DeliveryOperator, DeliveryOperatorAdmin)

