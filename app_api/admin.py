from django.contrib import admin
from .models import ServerResponse

class SeverResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'version', 'name' )
    #search_fields = ('article', )



admin.site.register(ServerResponse, SeverResponseAdmin)
